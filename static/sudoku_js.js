// Track the start time when the page loads
document.addEventListener('DOMContentLoaded', () => {
    const container = document.querySelector('.container');
    container.dataset.startTime = Date.now();
});

function trackSteps() {
    const container = document.querySelector('.container');
    let stepCount = parseInt(container.dataset.stepCount, 10);
    stepCount += 1;
    container.dataset.stepCount = stepCount;
}

// function checkSudoku() {
//     const cells = document.querySelectorAll('.cell input');
//     let values = [];

//     cells.forEach(cell => {
//         values.push(cell.value);
//     });

//     const container = document.querySelector('.container');
//     const startTime = parseInt(container.dataset.startTime, 10);
//     const endTime = Date.now();
//     const timeTaken = (endTime - startTime) / 1000; // Time in seconds
//     const stepCount = parseInt(container.dataset.stepCount, 10);

//     if (isValidSudoku(values)) {
//         const score = calculateScore(timeTaken, stepCount);
//         document.getElementById('result').textContent = `Score: ${score.toFixed(2)} (Time taken: ${timeTaken.toFixed(2)} seconds, Steps: ${stepCount})`;
//     } else {
//         document.getElementById('result').textContent = "Incorrect, try again.";
//     }
// }

function checkSudoku() {
    const cells = document.querySelectorAll('.cell input');
    let values = [];

    cells.forEach(cell => {
        values.push(cell.value);
    });

    const container = document.querySelector('.container');
    const startTime = parseInt(container.dataset.startTime, 10);
    const endTime = Date.now();
    const timeTaken = (endTime - startTime) / 1000; // Time in seconds
    const stepCount = parseInt(container.dataset.stepCount, 10);

    if (isValidSudoku(values)) {
        const score = calculateScore(timeTaken, stepCount);
        document.getElementById('result').textContent = `Score: ${score.toFixed(2)} (Time taken: ${timeTaken.toFixed(2)} seconds, Steps: ${stepCount})`;

        // Send score to backend
        fetch('/submit_sudoku_score', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ score: score.toFixed(2) })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                console.log('Score saved successfully');
            } else {
                console.error('Failed to save score');
            }
        });
    } else {
        document.getElementById('result').textContent = "Incorrect, try again.";
    }
}


function isValidSudoku(values) {
    const validSet = new Set(['1', '2', '3']);

    // Check if all values are in the range of 1 to 3
    for (let i = 0; i < values.length; i++) {
        if (!validSet.has(values[i])) {
            return false;
        }
    }

    // Check rows
    for (let i = 0; i < 3; i++) {
        const rowSet = new Set(values.slice(i * 3, i * 3 + 3));
        if (rowSet.size !== 3) {
            return false;
        }
    }

    // Check columns
    for (let i = 0; i < 3; i++) {
        const colSet = new Set([values[i], values[i + 3], values[i + 6]]);
        if (colSet.size !== 3) {
            return false;
        }
    }

    return true;
}

function calculateScore(timeTaken, stepCount) {
    // Define scoring parameters
    const maxScore = 100;
    const timePenalty = 0.5; // Points lost per second-    
    const stepPenalty = 0.2; // Points lost per step

    // Calculate penalties
    const timePenaltyScore = timePenalty * timeTaken;
    const stepPenaltyScore = stepPenalty * stepCount;

    // Calculate final score
    const score = Math.max(0, maxScore - timePenaltyScore - stepPenaltyScore);

    return score;
}