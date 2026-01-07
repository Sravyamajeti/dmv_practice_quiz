// This event listener waits for the HTML to be fully loaded before running our code.
// This ensures that all the elements we want to interact with (buttons, divs, etc.) actually exist.
document.addEventListener('DOMContentLoaded', () => {
    // We get references to the HTML elements we need to control.
    // 'document.getElementById' finds an element by its unique ID.
    const startBtn = document.getElementById('start-btn');
    const nextBtn = document.getElementById('next-btn');
    const restartBtn = document.getElementById('restart-btn');

    const startScreen = document.getElementById('start-screen');
    const questionScreen = document.getElementById('question-screen');
    const resultScreen = document.getElementById('result-screen');

    const questionText = document.getElementById('question-text');
    const optionsContainer = document.getElementById('options-container');
    const progressFill = document.getElementById('progress-fill');
    const questionNumberDisplay = document.getElementById('question-number');
    const scoreDisplay = document.getElementById('score-display');
    const navigationArea = document.getElementById('navigation-area');
    const finalScoreDisplay = document.getElementById('final-score');
    const resultMessage = document.getElementById('result-message');
    const resultsSummary = document.getElementById('results-summary');

    // These variables keep track of the quiz state.
    let questionIds = []; // Stores the list of question IDs to fetch.
    let userAnswers = []; // Stores the user's answers and the question details for the summary.
    let currentQuestionIndex = 0; // Keeps track of which question we are currently on (0 is the first one).
    let score = 0; // Keeps track of the user's score.
    let currentSelection = null; // Tracks the currently selected answer key
    let currentQuestion = null; // Tracks the current question object

    // We attach "click" event listeners to the buttons.
    // When a button is clicked, the specified function (startQuiz, nextQuestion) runs.
    startBtn.addEventListener('click', startQuiz);
    nextBtn.addEventListener('click', nextQuestion);
    restartBtn.addEventListener('click', startQuiz);

    // This function fetches the list of question IDs from our backend server.
    async function startQuiz() {
        startBtn.textContent = 'Loading...';
        startBtn.disabled = true;

        try {
            // We ask the server to start a quiz and give us a list of question IDs.
            // This is different from before: we get IDs first, then fetch questions one by one.
            const response = await fetch('/api/start_quiz');
            if (!response.ok) throw new Error('Failed to start quiz');
            questionIds = await response.json();

            if (questionIds.length === 0) {
                alert('No questions available.');
                return;
            }

            // Reset quiz state
            currentQuestionIndex = 0;
            score = 0;
            userAnswers = []; // Clear previous answers
            isAnswered = false;

            // Switch screens: Hide start and result screens, show question screen.
            startScreen.classList.add('hidden');
            resultScreen.classList.add('hidden');
            questionScreen.classList.remove('hidden');

            // Load the first question
            await showQuestion();
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to start quiz. Please try again.');
        } finally {
            startBtn.textContent = 'Start Quiz';
            startBtn.disabled = false;
        }
    }

    // This function fetches and displays the current question.
    async function showQuestion() {
        currentSelection = null;
        navigationArea.classList.add('hidden'); // Hide "Next" button until they answer

        // Show loading state or clear previous question
        questionText.textContent = 'Loading question...';
        optionsContainer.innerHTML = '';

        try {
            // Get the ID of the current question we need to show
            const questionId = questionIds[currentQuestionIndex];

            // Fetch the details for this specific question from the server
            const response = await fetch(`/api/question/${questionId}`);
            if (!response.ok) throw new Error('Failed to fetch question details');
            const question = await response.json();
            currentQuestion = question;

            // Update the text on the screen with the current question's data.
            questionText.textContent = question.question;
            questionNumberDisplay.textContent = `Question ${currentQuestionIndex + 1}/${questionIds.length}`;
            scoreDisplay.textContent = `Score: Hidden`; // Hide score during quiz so user doesn't know if they got it right yet

            // Update the visual progress bar.
            const progress = ((currentQuestionIndex) / questionIds.length) * 100;
            progressFill.style.width = `${progress}%`;

            // Create a button for each option (A, B, C).
            const options = ['A', 'B', 'C'];
            options.forEach(key => {
                const btn = document.createElement('button');
                btn.classList.add('option-btn');
                btn.textContent = question.options[key];
                btn.dataset.key = key; // Store which option this is (A, B, or C) on the button itself.
                // When clicked, call 'handleAnswer' with the chosen option.
                btn.addEventListener('click', () => handleAnswer(key, btn, question));
                optionsContainer.appendChild(btn);
            });

        } catch (error) {
            console.error('Error loading question:', error);
            questionText.textContent = 'Error loading question. Please try refreshing.';
        }
    }

    // This function handles what happens when a user clicks an answer.
    function handleAnswer(selectedKey, selectedBtn, question) {
        currentSelection = selectedKey;

        // Update visual selection
        const allBtns = optionsContainer.querySelectorAll('.option-btn');
        allBtns.forEach(btn => {
            btn.classList.remove('selected');
            if (btn.dataset.key === selectedKey) {
                btn.classList.add('selected');
            }
        });

        // Show the "Next" button.
        navigationArea.classList.remove('hidden');
    }

    // This function moves to the next question.
    async function nextQuestion() {
        if (!currentSelection || !currentQuestion) return;

        const isCorrect = currentSelection === currentQuestion.correctAnswer;

        if (isCorrect) {
            score++;
        }

        userAnswers.push({
            question: currentQuestion,
            selectedKey: currentSelection,
            isCorrect: isCorrect
        });

        currentQuestionIndex++;

        // If there are more questions, show the next one.
        if (currentQuestionIndex < questionIds.length) {
            await showQuestion();
        } else {
            // Otherwise, show the results.
            showResults();
        }
    }

    // This function shows the final score screen with detailed breakdown.
    function showResults() {
        questionScreen.classList.add('hidden');
        resultScreen.classList.remove('hidden');

        finalScoreDisplay.textContent = score;

        // Calculate percentage score.
        const percentage = (score / questionIds.length) * 100;
        if (percentage >= 80) {
            resultMessage.textContent = "Great job! You passed!";
            resultMessage.style.color = "var(--success-color)";
        } else {
            resultMessage.textContent = "Keep practicing. You need 80% to pass.";
            resultMessage.style.color = "var(--error-color)";
        }

        // Generate the detailed summary
        // This loops through all the answers the user gave and creates a list showing
        // the question, their answer, the correct answer, and the explanation.
        resultsSummary.innerHTML = '';
        userAnswers.forEach((item, index) => {
            const summaryItem = document.createElement('div');
            summaryItem.classList.add('summary-item');

            const isCorrectClass = item.isCorrect ? 'correct' : 'wrong';
            const statusText = item.isCorrect ? 'Correct' : 'Incorrect';

            summaryItem.innerHTML = `
                <div class="summary-header ${isCorrectClass}">
                    <span class="summary-number">#${index + 1}</span>
                    <span class="summary-status">${statusText}</span>
                </div>
                <p class="summary-question">${item.question.question}</p>
                <div class="summary-details">
                    <p><strong>Your Answer:</strong> ${item.question.options[item.selectedKey]} (${item.selectedKey})</p>
                    <p><strong>Correct Answer:</strong> ${item.question.options[item.question.correctAnswer]} (${item.question.correctAnswer})</p>
                    <p class="summary-explanation"><strong>Explanation:</strong> ${item.question.explanation}</p>
                </div>
            `;
            resultsSummary.appendChild(summaryItem);
        });
    }
});
