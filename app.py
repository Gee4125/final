import logging
logging.basicConfig(level=logging.DEBUG)
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template_string,render_template, request, redirect, url_for, session , jsonify
import os
import speech_recognition as sr
from pydub import AudioSegment
import io
import secrets
import tempfile
from datetime import datetime
import wave
from werkzeug.security import generate_password_hash, check_password_hash

def generate_secret_key():
    return secrets.token_hex(16)

app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = generate_secret_key()
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:admin123@localhost/cognitixdb'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:admin123@localhost/postgres'
app.config['SQLALCHEMY_DATABASE_URI'] ='postgresql://cognitixtest_user:oShwNT07lC62Gu7qXYkBtpDhqMCYU2Q9@dpg-cr9j9obv2p9s73b95pf0-a.oregon-postgres.render.com/cognitixtest'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(40), nullable=False)
    last_name = db.Column(db.String(40), nullable=False)
    gmail_id = db.Column(db.String(100), nullable=False, unique=True)
    phone = db.Column(db.String(15), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    address = db.Column(db.Text, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    # Relationships
    empathy_scores = db.relationship('EmpathyScore', backref='user', lazy=True)
    adaptability_scores = db.relationship('AdaptabilityScore', backref='user', lazy=True)
    # logical_scores = db.relationship('LogicalScore', backref='user', lazy=True)
    sudoku_scores=db.relationship('SudokuScore', backref='user', lazy=True)
    memory_scores=db.relationship('MemoryScore', backref='user', lazy=True)
    communication_scores = db.relationship('CommunicationScore', backref='user', lazy=True)

    def __init__(self, first_name, last_name, gmail_id, phone, dob, gender, address, password):
        self.first_name = first_name
        self.last_name = last_name
        self.gmail_id = gmail_id
        self.phone = phone
        self.dob = dob
        self.gender = gender
        self.address = address
        self.password = generate_password_hash(password)

class EmpathyScore(db.Model):
    __tablename__ = 'empathy_scores'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class AdaptabilityScore(db.Model):
    __tablename__ = 'adaptability_scores'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class SudokuScore(db.Model):
    __tablename__ = 'sudoku_scores'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    score = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class MemoryScore(db.Model):
    __tablename__ = 'memory_scores'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    score = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class CommunicationScore(db.Model):
    __tablename__ = 'communication_scores'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    score_type = db.Column(db.String(50), nullable=False)  # 'speech_recognition' or 'user_answers'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)




# Empathy scores for different options
empathy_scores = {
    'form_page_1': {'A': 1, 'B': 10, 'C': 5, 'D': 8},
    'form_page_2': {'A': 6, 'B': 10, 'C': 4, 'D': 1},
    'form_page_3': {'A': 2, 'B': 10, 'C': 3, 'D': 2},
    'form_page_4': {'A': 5, 'B': 8, 'C': 3, 'D': 1},
    'form_page_5': {'A': 7, 'B': 9, 'C': 4, 'D': 2}
}

# Evaluation metrics
# Evaluation metrics with more detailed categories
def evaluate_empathy(score):
    if score >= 31:
        return "Very High Empathy: You demonstrate an exceptional ability to understand and connect with others' emotions. Your empathy is deeply ingrained in your interactions and responses."
    elif score >= 26:
        return "High Empathy: You have a strong sense of empathy and are very attuned to the emotions and needs of others. You consistently show compassion and understanding."
    elif score >= 21:
        return "Moderate Empathy: You have a good level of empathy and usually respond well to others' emotions. You may occasionally miss some subtle cues but generally show understanding."
    elif score >= 16:
        return "Average Empathy: Your empathy is average. You are aware of others' feelings but may not always fully grasp their emotions or react as sensitively as possible."
    elif score >= 11:
        return "Low Empathy: You might find it challenging to understand and relate to others' feelings. There may be room for improvement in recognizing and responding to emotional cues."
    else:
        return "Very Low Empathy: You have significant difficulty in understanding and relating to others' emotions. Developing greater emotional awareness and sensitivity could benefit your relationships."

# Set the paths to the static files
image_path = 'C:\Dharsh\projects\full stack\proj_1\static\background-image.png'
audio_path = 'C:\Dharsh\projects\full stack\proj_1\static\audio-file.mp3'
bg_image_path = 'C:\Dharsh\projects\full stack\proj_1\static\background.png'
image1_path = 'C:\Dharsh\projects\full stack\proj_1\static\1_k.jpeg'
image2_path = 'C:\Dharsh\projects\full stack\proj_1\static\2_k.jpeg'
audio_path = 'C:\Dharsh\projects\full stack\proj_1\static\audio.mp3'

# Empathy scores for different options
adaptability_scores = {
    'scenario_1': {'A': 2, 'B': 8, 'C': 5, 'D': 3},
    'scenario_2': {'A': 2, 'B': 8, 'C': 5, 'D': 3},
    'scenario_3': {'A': 2, 'B': 8, 'C': 5, 'D': 6},
    'scenario_4': {'A': 2, 'B': 8, 'C': 5, 'D': 3},
    'scenario_5': {'A': 2, 'B': 8, 'C': 3, 'D': 5}
}


# Evaluation metrics
def evaluate_adaptability(score):
    if score >= 35:
        return "Highly Adaptable - You excel in adapting to new situations and changes. You are flexible, resilient, and thrive in dynamic environments."
    elif score >= 25:
        return "Moderately Adaptable - You are fairly adaptable and can handle changes well, though there may be times when you find adjustments challenging."
    elif score >= 15:
        return "Average Adaptability - Your adaptability is average. You manage changes adequately but may feel uncomfortable with significant or sudden shifts."
    elif score >= 5:
        return "Low Adaptability - You might find it challenging to adapt to new situations and changes. Working on being more open to new experiences could help improve your adaptability."
    else:
        return "You struggle significantly with adapting to change. Developing greater flexibility and resilience can help you navigate changes more effectively."



# Initialize the recognizer
recognizer = sr.Recognizer()

# Texts for the user to read
expected_text1 = "The quick brown fox jumps over the lazy dog"
expected_text2 = "Pack my box with five dozen liquor jugs"

@app.route('/')
def main_page():
    return render_template('MAIN_PAGE_HTML.html')

@app.route('/login_page')
def login_page():
    return render_template('LOGIN_SIGNUP_HTML.html')

# @app.route('/login', methods=['POST'])
# def login():
#     gmail_id = request.form['gmail-id']
#     password = request.form['password']

#     user = User.query.filter_by(gmail_id=gmail_id).first()
    
#     if user and check_password_hash(user.password, password):
#         return "Login successful"
#     else:
#         return "Invalid credentials"
#     # Add your login logic here
#     return redirect(url_for('topics_page'))

@app.route('/login', methods=['POST'])
def login():
    try:
        gmail_id = request.form['gmail-id']
        password = request.form['password']

        user = User.query.filter_by(gmail_id=gmail_id).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('topics_page'))
        else:
            return "Invalid credentials", 401
    except Exception as e:
        return f"An error occurred: {str(e)}", 500

    

# @app.route('/signup', methods=['POST'])
# def signup():
#     first_name = request.form['first-name']
#     last_name = request.form['last-name']
#     gmail_id = request.form['gmail-id']
#     phone = request.form['phone']
#     dob = request.form['dob']
#     gender = request.form['gender']
#     address = request.form['address']
#     password = request.form['password']


#     new_user = User(first_name, last_name, gmail_id, phone, dob, gender, address, password)
#     db.session.add(new_user)
#     db.session.commit()

#     # Add your signup logic here
#     return redirect(url_for('topics'))

# @app.route('/signup', methods=['POST'])
# def signup():
#     try:
#         first_name = request.form['first-name']
#         last_name = request.form['last-name']
#         gmail_id = request.form['gmail-id']
#         phone = request.form['phone']
#         dob = request.form['dob']
#         gender = request.form['gender']
#         address = request.form['address']
#         password = request.form['password']

#         new_user = User(first_name, last_name, gmail_id, phone, dob, gender, address, password)
#         db.session.add(new_user)
#         db.session.commit()

#         return redirect(url_for('topics_page'))
        
        
#     except Exception as e:
#         db.session.rollback()
#         return f"An error occurred: {str(e)}", 500

@app.route('/signup', methods=['POST'])
def signup():
    try:
        first_name = request.form['first-name']
        last_name = request.form['last-name']
        gmail_id = request.form['gmail-id']
        phone = request.form['phone']
        dob = request.form['dob']
        gender = request.form['gender']
        address = request.form['address']
        password = request.form['password']

        new_user = User(first_name, last_name, gmail_id, phone, dob, gender, address, password)
        db.session.add(new_user)
        db.session.commit()

        # Redirect the user to the login page (GET request)
        return redirect(url_for('login_page'))  # Ensure you have a login page route for the form submission
    except Exception as e:
        return f"An error occurred: {str(e)}", 500



@app.route('/topics')
def topics_page():
    return render_template('TOPICS_PAGE_HTML.html')

@app.route('/topics/<topic_name>')
def topic_page(topic_name):
    # Placeholder logic for topic page content
    return f"This is the page for {topic_name.capitalize()}."

@app.route("/index")
def index_f():
    return render_template('FIRST_PAGE.html')

@app.route('/form_page_1', methods=['GET', 'POST'])
def form_page_1():
    if request.method == 'POST':
        selected_option = request.form.get('response')
        score = empathy_scores['form_page_1'].get(selected_option, 0)
        session['total_score'] = score
        return redirect(url_for('second_page'))
    return render_template('form_html1.html')

@app.route('/second_page')
def second_page():
    return render_template('second_html.html')

@app.route('/form_page_2', methods=['GET', 'POST'])
def form_page_2():
    if request.method == 'POST':
        selected_option = request.form.get('response')
        score = empathy_scores['form_page_2'].get(selected_option, 0)
        session['total_score'] += score
        return redirect(url_for('third_page'))
    return render_template('form_html2.html')

@app.route('/third_page')
def third_page():
    return render_template('third_html.html')

@app.route('/form_page_3', methods=['GET', 'POST'])
def form_page_3():
    if request.method == 'POST':
        selected_option = request.form.get('response')
        score = empathy_scores['form_page_3'].get(selected_option, 0)
        session['total_score'] += score
        return redirect(url_for('fourth_page'))
    return render_template('form_html3.html')

@app.route('/fourth_page')
def fourth_page():
    return render_template('fourth_html.html')

@app.route('/form_page_4', methods=['GET', 'POST'])
def form_page_4():
    if request.method == 'POST':
        selected_option = request.form.get('response')
        score = empathy_scores['form_page_4'].get(selected_option, 0)
        session['total_score'] += score
        return redirect(url_for('fifth_page'))
    return render_template('form_html4.html')

@app.route('/fifth_page')
def fifth_page():
    return render_template('five_html.html')

# @app.route('/form_page_5', methods=['GET', 'POST'])
# def form_page_5():
#     if request.method == 'POST':
#         selected_option = request.form.get('response')
#         score = empathy_scores['form_page_5'].get(selected_option, 0)
#         session['total_score'] += score
#         return redirect(url_for('result_page'))
#     return render_template('form_html5.html')

# @app.route('/form_page_5', methods=['GET', 'POST'])
# def form_page_5():
#     if request.method == 'POST':
#         selected_option = request.form.get('response')
#         score = empathy_scores['form_page_5'].get(selected_option, 0)
#         session['total_score'] += score

#         # Save the score to the database
#         user_id = session.get('user_id')
#         if user_id:
#             empathy_score = EmpathyScore(user_id=user_id, score=session['total_score'])
#             db.session.add(empathy_score)
#             db.session.commit()

#         return redirect(url_for('result_page'))
#     return render_template('form_html5.html')

@app.route('/form_page_5', methods=['GET', 'POST'])
def form_page_5():
    if request.method == 'POST':
        selected_option = request.form.get('response')
        score = empathy_scores['form_page_5'].get(selected_option, 0)
        session['total_score'] += score

        # Save the score to the database
        user_id = session.get('user_id')
        if user_id:
            empathy_score = EmpathyScore(user_id=user_id, score=session['total_score'])
            db.session.add(empathy_score)
            db.session.commit()

        return redirect(url_for('result_page'))
    return render_template('form_html5.html')

@app.route('/result_page')
def result_page():
    total_score = session.get('total_score', 0)
    result_text = evaluate_empathy(total_score)
    return render_template('result_html_template.html', total_score=total_score, result_text=result_text)
# Routes for pages - adaptability
@app.route('/starting')
def starting_page():
    return render_template('FIRST_PAGE_A.html')

@app.route('/form_page_1_a', methods=['GET', 'POST'])
def form_page_1_a():
    if request.method == 'POST':
        session['response_1'] = request.form['response']
        return redirect(url_for('second_page_a'))
    return render_template('form_html1_a.html')

@app.route('/second_page_a')
def second_page_a():
    return render_template('second_html_a.html')

@app.route('/form_page_2_a', methods=['GET', 'POST'])
def form_page_2_a():
    if request.method == 'POST':
        session['response_2'] = request.form['response']
        return redirect(url_for('third_page_a'))
    return render_template('form_html2_a.html')

@app.route('/third_page_a')
def third_page_a():
    return render_template('third_html_a.html')

@app.route('/form_page_3_a', methods=['GET', 'POST'])
def form_page_3_a():
    if request.method == 'POST':
        session['response_3'] = request.form['response']
        return redirect(url_for('fourth_page_a'))
    return render_template('form_html3_a.html')

@app.route('/fourth_page_a')
def fourth_page_a():
    return render_template('fourth_html_a.html')

@app.route('/form_page_4_a', methods=['GET', 'POST'])
def form_page_4_a():
    if request.method == 'POST':
        session['response_4'] = request.form['response']
        return redirect(url_for('fifth_page_a'))
    return render_template('form_html4_a.html')

@app.route('/fifth_page_a')
def fifth_page_a():
    return render_template('fifth_html_a.html')

# @app.route('/form_page_5_a', methods=['GET', 'POST'])
# def form_page_5_a():
#     if request.method == 'POST':
#         session['response_5'] = request.form['response']
#         return redirect(url_for('results_a'))
#     return render_template('form_html5_a.html')

# @app.route('/form_page_5_a', methods=['GET', 'POST'])
# def form_page_5_a():
#     if request.method == 'POST':
#         session['response_5'] = request.form['response']

#         responses = [
#             session.get('response_1'),
#             session.get('response_2'),
#             session.get('response_3'),
#             session.get('response_4'),
#             session.get('response_5')
#         ]

#         total_score = sum(
#             adaptability_scores[f'scenario_{i+1}'].get(response, 0)
#             for i, response in enumerate(responses)
#         )

#         # Save the score to the database
#         user_id = session.get('user_id')
#         if user_id:
#             adaptability_score = AdaptabilityScore(user_id=user_id, score=total_score)
#             db.session.add(adaptability_score)
#             db.session.commit()

#         return redirect(url_for('results_a'))
#     return render_template('form_html5_a.html')

@app.route('/form_page_5_a', methods=['GET', 'POST'])
def form_page_5_a():
    if request.method == 'POST':
        session['response_5'] = request.form['response']

        responses = [
            session.get('response_1'),
            session.get('response_2'),
            session.get('response_3'),
            session.get('response_4'),
            session.get('response_5')
        ]

        total_score = sum(
            adaptability_scores[f'scenario_{i+1}'].get(response, 0)
            for i, response in enumerate(responses)
        )

        # Save the score to the database
        user_id = session.get('user_id')
        if user_id:
            adaptability_score = AdaptabilityScore(user_id=user_id, score=total_score)
            db.session.add(adaptability_score)
            db.session.commit()

        return redirect(url_for('results_a'))
    return render_template('form_html5_a.html')


@app.route('/results_a')
def results_a():
    responses = [
        session.get('response_1'),
        session.get('response_2'),
        session.get('response_3'),
        session.get('response_4'),
        session.get('response_5')
    ]

    total_score = sum(
        adaptability_scores[f'scenario_{i+1}'].get(response, 0)
        for i, response in enumerate(responses)
    )

    adaptability_rating = evaluate_adaptability(total_score)

    return render_template('result_html_a.html', adaptability_score=total_score, adaptability_rating=adaptability_rating)
@app.route('/logic_first')
def Logic_first():
    return render_template('sudoku_html.html')

@app.route('/memory_game')
def memory_game():
    return render_template('memory_html.html')

# @app.route('/static/style.css')
# def serve_css():
#     return sudoku_css, 200, {'Content-Type': 'text/css'}

# @app.route('/static/script.js')
# def serve_js():
#     return sudoku_js, 200, {'Content-Type': 'application/javascript'}

# @app.route('/static/memory_style.css')
# def serve_memory_css():
#     return memory_css, 200, {'Content-Type': 'text/css'}

# @app.route('/static/memory_script.js')
# def serve_memory_js():
#     return memory_js, 200, {'Content-Type': 'application/javascript'}
@app.route('/sudoku_css')
def serve_css():
    return render_template('sudoku_css.css')

@app.route('/sudoku_js')
def serve_js():
    return render_template('sudoku_js.js')

@app.route('/memory_style')
def serve_memory_css():
    return render_template('memory_css.css')

@app.route('/memory_script')
def serve_memory_js():
    return render_template('memory_js.js')

@app.route('/submit_sudoku_score', methods=['POST'])
def submit_sudoku_score():
    logging.debug('Sudoku score submission route accessed')
    data = request.json
    score = data.get('score')
    user_id = session.get('user_id')

    if user_id:
        logging.debug(f'User ID: {user_id}')
        sudoku_score = SudokuScore(user_id=user_id, score=score)
        db.session.add(sudoku_score)
        try:
            db.session.commit()
            return jsonify({'status': 'success', 'message': 'Score saved successfully'})
        except Exception as e:
            db.session.rollback()
            logging.error(f'Database commit error: {str(e)}')
            return jsonify({'status': 'error', 'message': 'Failed to save score'}), 500
    else:
        logging.debug('User not logged in')
        return jsonify({'status': 'error', 'message': 'User not logged in'}), 401

@app.route('/submit_memory_score', methods=['POST'])
def submit_memory_score():
    data = request.json
    score = data.get('score')
    user_id = session.get('user_id')

    if user_id:
        memory_score = MemoryScore(user_id=user_id, score=score)
        db.session.add(memory_score)
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Score saved successfully'})
    else:
        return jsonify({'status': 'error', 'message': 'User not logged in'}), 401



@app.route('/page1')
def page1():
    return render_template('page1_html_s.html')

@app.route('/speech-recognition')
def index():
    return render_template('index_html_s.html', expected_text1=expected_text1, expected_text2=expected_text2)

# @app.route('/record', methods=['POST'])
# def record():
#     audio_file = request.files['audio']

#     # Convert the audio file to WAV format
#     audio = AudioSegment.from_file(audio_file)
#     audio_wav = io.BytesIO()
#     audio.export(audio_wav, format="wav")
#     audio_wav.seek(0)

#     # Save the WAV file temporarily to check it
#     with open("/tmp/test.wav", "wb") as f:
#         f.write(audio_wav.getvalue())

#     # Recognize speech using speech_recognition
#     try:
#         with sr.AudioFile(audio_wav) as source:
#             audio_data = recognizer.record(source)
#             recognized_text = recognizer.recognize_google(audio_data)
#             print(f"You said: {recognized_text}")

#             # Compare the recognized speech with the expected text
#             accuracy1 = calculate_accuracy(recognized_text, expected_text1)
#             accuracy2 = calculate_accuracy(recognized_text, expected_text2)

#             return render_template('result_html.html', recognized_text=recognized_text, accuracy1=accuracy1, accuracy2=accuracy2)
#     except sr.UnknownValueError:
#         return "Google Speech Recognition could not understand audio"
#     except sr.RequestError as e:
#         return f"Could not request results from Google Speech Recognition service; {e}"

# @app.route('/record', methods=['POST'])
# def record():
#     audio_file = request.files['audio']

#     # Convert the audio file to WAV format
#     audio = AudioSegment.from_file(audio_file, format="webm")
#     audio_wav = io.BytesIO()
#     audio.export(audio_wav, format="wav")
#     audio_wav.seek(0)

#     # Save the WAV file temporarily to check it
#     with open("/tmp/test.wav", "wb") as f:
#         f.write(audio_wav.getvalue())

#     # Recognize speech using speech_recognition
#     try:
#         with sr.AudioFile(audio_wav) as source:
#             audio_data = recognizer.record(source)
#             recognized_text = recognizer.recognize_google(audio_data, language="en-US")
#             print(f"You said: {recognized_text}")

#             # Compare the recognized speech with the expected text
#             accuracy1 = calculate_accuracy(recognized_text, expected_text1)
#             accuracy2 = calculate_accuracy(recognized_text, expected_text2)

#             return render_template('result_html.html', recognized_text=recognized_text, accuracy1=accuracy1, accuracy2=accuracy2)
#     except sr.UnknownValueError:
#         return "Google Speech Recognition could not understand audio"
#     except sr.RequestError as e:
#         return f"Could not request results from Google Speech Recognition service; {e}"

# @app.route('/record', methods=['POST'])
# def record():
#     if 'audio' not in request.files:
#         return "No audio file part", 400

#     audio_file = request.files['audio']
    
#     # Save the uploaded file to a temporary location
#     temp_audio_path = tempfile.mktemp(suffix=".mp3")
#     audio_file.save(temp_audio_path)
    
#     # Convert the audio to WAV format using pydub
#     try:
#         audio = AudioSegment.from_file(temp_audio_path)
#         wav_audio_path = temp_audio_path.replace(".mp3", ".wav")
#         audio.export(wav_audio_path, format="wav")
        
#         # Now process the WAV audio with speech_recognition
#         recognizer = sr.Recognizer()
#         with sr.AudioFile(wav_audio_path) as source:
#             audio_data = recognizer.record(source)
#             try:
#                 text = recognizer.recognize_google(audio_data)
#                 return f"Recognized Text: {text}"
#             except sr.UnknownValueError:
#                 return "Google Speech Recognition could not understand audio"
#             except sr.RequestError:
#                 return "Could not request results from Google Speech Recognition service"
#     except Exception as e:
#         return f"Error: {str(e)}"
#     finally:
#         os.remove(temp_audio_path)
#         if os.path.exists(wav_audio_path):
#             os.remove(wav_audio_path)

# @app.route('/record', methods=['POST'])
# def record():
#     if 'audio' not in request.files:
#         return "No audio file part", 400

#     audio_file = request.files['audio']
    
#     # Save the uploaded file to a temporary location
#     temp_audio_path = tempfile.mktemp(suffix=".mp3")
#     audio_file.save(temp_audio_path)
    
#     try:
#         # Convert the audio to WAV format using pydub
#         audio = AudioSegment.from_file(temp_audio_path)
#         wav_audio_path = temp_audio_path.replace(".mp3", ".wav")
#         audio.export(wav_audio_path, format="wav")
        
#         # Process the WAV audio with speech_recognition
#         recognizer = sr.Recognizer()
#         with sr.AudioFile(wav_audio_path) as source:
#             audio_data = recognizer.record(source)
#             try:
#                 recognized_text = recognizer.recognize_google(audio_data)
#                 print(f"Recognized Text: {recognized_text}")

#                 # Expected texts for comparison
#                 expected_text1 = "Expected sentence one"
#                 expected_text2 = "Expected sentence two"

#                 # Calculate accuracy for each expected text
#                 accuracy1 = calculate_accuracy(recognized_text, expected_text1)
#                 accuracy2 = calculate_accuracy(recognized_text, expected_text2)
#                 print(f"Accuracy1: {accuracy1:.2f}%")
#                 print(f"Accuracy2: {accuracy2:.2f}%")

#                 # Render the result to the template
#                 return render_template('result_html.html', recognized_text=recognized_text, accuracy1=accuracy1, accuracy2=accuracy2)
#             except sr.UnknownValueError:
#                 return "Google Speech Recognition could not understand audio"
#             except sr.RequestError:
#                 return "Could not request results from Google Speech Recognition service"
#     except Exception as e:
#         return f"Error: {str(e)}"
#     finally:
#         os.remove(temp_audio_path)
#         if os.path.exists(wav_audio_path):
#             os.remove(wav_audio_path)


# def calculate_accuracy(recognized_text, expected_text):
#     recognized_words = recognized_text.lower().split()
#     expected_words = expected_text.lower().split()
#     matching_words = sum(1 for i, word in enumerate(recognized_words) if i < len(expected_words) and word == expected_words[i])
#     accuracy = matching_words / len(expected_words) * 100
#     return accuracy



# @app.route('/record', methods=['POST'])
# def record():
#     if 'audio' not in request.files:
#         return "No audio file part", 400

#     audio_file = request.files['audio']
    
#     # Save the uploaded file to a temporary location
#     temp_audio_path = tempfile.mktemp(suffix=".mp3")
#     audio_file.save(temp_audio_path)
    
#     # Convert the audio to WAV format using pydub
#     try:
#         audio = AudioSegment.from_file(temp_audio_path)
#         wav_audio_path = temp_audio_path.replace(".mp3", ".wav")
#         audio.export(wav_audio_path, format="wav")
        
#         # Now process the WAV audio with speech_recognition
#         recognizer = sr.Recognizer()
#         with sr.AudioFile(wav_audio_path) as source:
#             audio_data = recognizer.record(source)
#             try:
#                 recognized_text = recognizer.recognize_google(audio_data)
#                 expected_text1 = "The quick brown fox jumps over the lazy dog"
#                 expected_text2 = "Pack my box with five dozen liquor jugs"

#                 accuracy1 = calculate_accuracy(recognized_text, expected_text1)
#                 accuracy2 = calculate_accuracy(recognized_text, expected_text2)

#                 return render_template('result_html.html', recognized_text=recognized_text, accuracy1=accuracy1, accuracy2=accuracy2)
#             except sr.UnknownValueError:
#                 return "Google Speech Recognition could not understand audio"
#             except sr.RequestError as e:
#                 return f"Could not request results from Google Speech Recognition service; {e}"
#     except Exception as e:
#         return f"Error: {str(e)}"
#     finally:
#         os.remove(temp_audio_path)
#         if os.path.exists(wav_audio_path):
#             os.remove(wav_audio_path)

# @app.route('/record', methods=['POST'])
# def record():
#     if 'audio' not in request.files:
#         return "No audio file part", 400

#     audio_file = request.files['audio']
    
#     # Save the uploaded file to a temporary location
#     temp_audio_path = tempfile.mktemp(suffix=".mp3")
#     audio_file.save(temp_audio_path)
    
#     # Convert the audio to WAV format using pydub
#     try:
#         audio = AudioSegment.from_file(temp_audio_path)
#         wav_audio_path = temp_audio_path.replace(".mp3", ".wav")
#         audio.export(wav_audio_path, format="wav")
        
#         # Now process the WAV audio with speech_recognition
#         recognizer = sr.Recognizer()
#         with sr.AudioFile(wav_audio_path) as source:
#             audio_data = recognizer.record(source)
#             try:
#                 recognized_text = recognizer.recognize_google(audio_data)
#                 expected_text1 = "The quick brown fox jumps over the lazy dog"
#                 expected_text2 = "Pack my box with five dozen liquor jugs"

#                 accuracy1 = calculate_accuracy(recognized_text, expected_text1)
#                 accuracy2 = calculate_accuracy(recognized_text, expected_text2)

#                 return render_template('result_html.html', recognized_text=recognized_text, accuracy1=accuracy1, accuracy2=accuracy2)
#             except sr.UnknownValueError:
#                 return "Google Speech Recognition could not understand audio"
#             except sr.RequestError as e:
#                 return f"Could not request results from Google Speech Recognition service; {e}"
#     except Exception as e:
#         return f"Error: {str(e)}"
#     finally:
#         os.remove(temp_audio_path)
#         if os.path.exists(wav_audio_path):
#             os.remove(wav_audio_path)


@app.route('/record', methods=['POST'])
def record():
    if 'audio' not in request.files:
        return "No audio file part", 400

    audio_file = request.files['audio']
    temp_audio_path = tempfile.mktemp(suffix=".mp3")
    audio_file.save(temp_audio_path)

    try:
        audio = AudioSegment.from_file(temp_audio_path)
        wav_audio_path = temp_audio_path.replace(".mp3", ".wav")
        audio.export(wav_audio_path, format="wav")

        with sr.AudioFile(wav_audio_path) as source:
            audio_data = recognizer.record(source)
            recognized_text = recognizer.recognize_google(audio_data)

            accuracy1 = calculate_accuracy(recognized_text, expected_text1)
            accuracy2 = calculate_accuracy(recognized_text, expected_text2)

            user_id = session.get('user_id')
            if user_id:
                speech_recognition_score = CommunicationScore(user_id=user_id, score=(accuracy1 + accuracy2) / 2, score_type='speech_recognition')
                db.session.add(speech_recognition_score)
                db.session.commit()

            return render_template('result_html.html', recognized_text=recognized_text, accuracy1=accuracy1, accuracy2=accuracy2)
    except sr.UnknownValueError:
        return "Google Speech Recognition could not understand audio"
    except sr.RequestError as e:
        return f"Could not request results from Google Speech Recognition service; {e}"
    finally:
        os.remove(temp_audio_path)
        if os.path.exists(wav_audio_path):
            os.remove(wav_audio_path)

def calculate_accuracy(recognized_text, expected_text):
    recognized_words = recognized_text.lower().split()
    expected_words = expected_text.lower().split()

    print(f"Recognized Words: {recognized_words}")
    print(f"Expected Words: {expected_words}")

    matching_words = 0

    for i in range(min(len(recognized_words), len(expected_words))):
        print(f"Comparing: '{recognized_words[i]}' with '{expected_words[i]}'")
        if recognized_words[i] == expected_words[i]:
            matching_words += 1

    accuracy = (matching_words / len(expected_words)) * 100 if expected_words else 0
    print(f"Calculated accuracy: {accuracy}%")
    return accuracy



@app.route('/result')
def result():
    # Process the results and render the result page
    result_text1 = '{{ accuracy1 }}%'  # Process text 1 result here
    result_text2 = '{{ accuracy1 }}%'  # Process text 2 result here
    return render_template('result_html.html', result_text1=result_text1, result_text2=result_text2)

@app.route('/next')
def next_page():
    return render_template('page1_html.html')

@app.route('/page2')
def page2():
    return render_template('page2_html.html')

# @app.route('/submit_answers', methods=['POST'])
# def submit_answers():
#     user_answers = request.json['answers']
#     correct_answers = [
#         "c",  # the string
#         "d",  # soar high
#         "b",  # follow a set of rules
#         "a",  # track
#         "b",  # chaos
#         "c"   # the importance of discipline
#     ]
#     score = sum(1 for user, correct in zip(user_answers, correct_answers) if user.lower() == correct)
#     return jsonify({'score': score, 'total': len(correct_answers)})

# @app.route('/submit_answers', methods=['POST'])
# def submit_answers():
#     user_answers = request.json['answers']
#     correct_answers = [
#         "c",  # the string
#         "d",  # soar high
#         "b",  # follow a set of rules
#         "a",  # track
#         "b",  # chaos
#         "c"   # the importance of discipline
#     ]
#     score = sum(1 for user, correct in zip(user_answers, correct_answers) if user.lower() == correct)

#     # Save the score to the database
#     user_id = session.get('user_id')
#     if user_id:
#         logical_score = LogicalScore(user_id=user_id, score=score)
#         db.session.add(logical_score)
#         db.session.commit()

#     return jsonify({'score': score, 'total': len(correct_answers)})

@app.route('/submit_answers', methods=['POST'])
def submit_answers():
    user_answers = request.json['answers']
    correct_answers = ["c", "d", "b", "a", "b", "c"]
    score = sum(1 for user, correct in zip(user_answers, correct_answers) if user.lower() == correct)

    user_id = session.get('user_id')
    if user_id:
        user_answers_score = CommunicationScore(user_id=user_id, score=score, score_type='user_answers')
        db.session.add(user_answers_score)
        db.session.commit()

    return jsonify({'score': score, 'total': len(correct_answers)})

@app.route('/final_page')
def final_page():
    return render_template('FINAL_PAGE_HTML.html')

# @app.route('/final')
# def final():
#     user_id = session.get('user_id')
#     if not user_id:
#         return redirect(url_for('login_page'))

#     user = User.query.get(user_id)
#     if not user:
#         return "User not found", 404

#     empathy_scores = EmpathyScore.query.filter_by(user_id=user_id).all()
#     adaptability_scores = AdaptabilityScore.query.filter_by(user_id=user_id).all()
#     sudoku_scores = SudokuScore.query.filter_by(user_id=user_id).all()
#     memory_scores = MemoryScore.query.filter_by(user_id=user_id).all()
#     communication_scores = CommunicationScore.query.filter_by(user_id=user_id).all()

#     return render_template('final.html', user=user, empathy_scores=empathy_scores, adaptability_scores=adaptability_scores, sudoku_scores=sudoku_scores, memory_scores=memory_scores, communication_scores=communication_scores)


# @app.route('/about_you')
# def about_you():
#     user_id = session.get('user_id')
#     if not user_id:
#         return redirect(url_for('login_page'))

#     user = User.query.get(user_id)
#     if not user:
#         return "User not found", 404

#     empathy_scores = EmpathyScore.query.filter_by(user_id=user_id).all()
#     adaptability_scores = AdaptabilityScore.query.filter_by(user_id=user_id).all()
#     sudoku_scores = SudokuScore.query.filter_by(user_id=user_id).all()
#     memory_scores = MemoryScore.query.filter_by(user_id=user_id).all()
#     communication_scores = CommunicationScore.query.filter_by(user_id=user_id).all()

#     return render_template('aboutyou.html', user=user, empathy_scores=empathy_scores, adaptability_scores=adaptability_scores, sudoku_scores=sudoku_scores, memory_scores=memory_scores, communication_scores=communication_scores)

@app.route('/final')
def final():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login_page'))

    user = User.query.get(user_id)
    if not user:
        return "User not found", 404

    empathy_scores = EmpathyScore.query.filter_by(user_id=user_id).all()
    adaptability_scores = AdaptabilityScore.query.filter_by(user_id=user_id).all()
    sudoku_scores = SudokuScore.query.filter_by(user_id=user_id).all()
    memory_scores = MemoryScore.query.filter_by(user_id=user_id).all()
    communication_scores = CommunicationScore.query.filter_by(user_id=user_id).all()

    return render_template('final.html', user=user, empathy_scores=empathy_scores, adaptability_scores=adaptability_scores, sudoku_scores=sudoku_scores, memory_scores=memory_scores, communication_scores=communication_scores)

# @app.route('/about_you')
# def about_you():
#     user_id = session.get('user_id')
#     if not user_id:
#         return redirect(url_for('login_page'))

#     user = User.query.get(user_id)
#     if not user:
#         return "User not found", 404

#     empathy_scores = EmpathyScore.query.filter_by(user_id=user_id).all()
#     adaptability_scores = AdaptabilityScore.query.filter_by(user_id=user_id).all()
#     sudoku_scores = SudokuScore.query.filter_by(user_id=user_id).all()
#     memory_scores = MemoryScore.query.filter_by(user_id=user_id).all()
#     communication_scores = CommunicationScore.query.filter_by(user_id=user_id).all()

#     return render_template('aboutyou.html', user=user, empathy_scores=empathy_scores, adaptability_scores=adaptability_scores, sudoku_scores=sudoku_scores, memory_scores=memory_scores, communication_scores=communication_scores)

@app.route('/about_you')
def about_you():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login_page'))

    user = User.query.get(user_id)
    if not user:
        return "User not found", 404

    empathy_scores = [score.score for score in EmpathyScore.query.filter_by(user_id=user_id).all()]
    adaptability_scores = [score.score for score in AdaptabilityScore.query.filter_by(user_id=user_id).all()]
    sudoku_scores = SudokuScore.query.filter_by(user_id=user_id).first().score
    memory_scores = MemoryScore.query.filter_by(user_id=user_id).first().score
    communication_scores = [score.score for score in CommunicationScore.query.filter_by(user_id=user_id).all()]

    return render_template(
        'aboutyou.html',
        user=user,
        empathy_scores=empathy_scores,
        adaptability_scores=adaptability_scores,
        sudoku_score=sudoku_scores,
        memory_score=memory_scores,
        communication_scores=communication_scores
    )


if __name__ == "__main__":
    app.run(debug=True)