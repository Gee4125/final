const cardsArray = ['🍎', '🍌', '🍇', '🍉', '🍓', '🍒', '🍍', '🍑', '🍎', '🍌', '🍇', '🍉', '🍓', '🍒', '🍍', '🍑'];
let shuffledCards, flippedCards, matchedCards, gameBoard, attempts, score;

// function startGame() {
//     shuffledCards = shuffle(cardsArray.slice());
//     flippedCards = [];
//     matchedCards = [];
//     attempts = 0;
//     score = 0;
//     gameBoard = document.getElementById('game-board');
//     gameBoard.innerHTML = '';

//     shuffledCards.forEach((card, index) => {
//         const cardElement = document.createElement('div');
//         cardElement.classList.add('card');
//         cardElement.dataset.card = card;
//         cardElement.dataset.index = index;
//         cardElement.innerHTML = card;
//         cardElement.addEventListener('click', flipCard);
//         gameBoard.appendChild(cardElement);
//     });

//     document.getElementById('message').textContent = '';
// }


function startGame() {
    shuffledCards = shuffle(cardsArray.slice());
    flippedCards = [];
    matchedCards = [];
    attempts = 0;
    score = 0;
    gameBoard = document.getElementById('game-board');
    gameBoard.innerHTML = '';

    shuffledCards.forEach((card, index) => {
        const cardElement = document.createElement('div');
        cardElement.classList.add('card');
        cardElement.dataset.card = card;
        cardElement.dataset.index = index;
        cardElement.innerHTML = card;
        cardElement.addEventListener('click', flipCard);
        gameBoard.appendChild(cardElement);
    });

    document.getElementById('message').textContent = '';
}

function shuffle(array) {
    for (let i = array.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [array[i], array[j]] = [array[j], array[i]];
    }
    return array;
}

function flipCard(event) {
    const clickedCard = event.currentTarget;
    if (flippedCards.length < 2 && !clickedCard.classList.contains('flipped') && !clickedCard.classList.contains('matched')) {
        clickedCard.classList.add('flipped');
        flippedCards.push(clickedCard);

        if (flippedCards.length === 2) {
            checkForMatch();
        }
    }
}

// function checkForMatch() {
//     const [card1, card2] = flippedCards;
//     attempts++;

//     if (card1.dataset.card === card2.dataset.card) {
//         card1.classList.add('matched');
//         card2.classList.add('matched');
//         matchedCards.push(card1, card2);

//         if (matchedCards.length === cardsArray.length) {
//             score = Math.max(100 - attempts, 0); // Example scoring formula
//             document.getElementById('message').textContent = `Congratulations! You matched all the cards with a score of ${score}!`;
//         }
//     } else {
//         setTimeout(() => {
//             card1.classList.remove('flipped');
//             card2.classList.remove('flipped');
//         }, 1000);
//     }

//     flippedCards = [];
// }

function checkForMatch() {
    const [card1, card2] = flippedCards;
    attempts++;

    if (card1.dataset.card === card2.dataset.card) {
        card1.classList.add('matched');
        card2.classList.add('matched');
        matchedCards.push(card1, card2);

        if (matchedCards.length === cardsArray.length) {
            score = Math.max(100 - attempts, 0); // Example scoring formula
            document.getElementById('message').textContent = `Congratulations! You matched all the cards with a score of ${score}!`;

            // Send score to backend
            fetch('/submit_memory_score', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ score: score })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    console.log('Score saved successfully');
                } else {
                    console.error('Failed to save score');
                }
            });
        }
    } else {
        setTimeout(() => {
            card1.classList.remove('flipped');
            card2.classList.remove('flipped');
        }, 1000);
    }

    flippedCards = [];
}

startGame();
