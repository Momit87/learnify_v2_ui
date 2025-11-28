// Global object to store selected answers
let selectedAnswers = {};

// File upload logic
let uploadedFile = null;

function showLoadingSpinner() {
    document.getElementById("loading-spinner").style.display = "block";
}

function hideLoadingSpinner() {
    document.getElementById("loading-spinner").style.display = "none";
}

function uploadFile() {
    const fileInput = document.getElementById('file-upload');
    uploadedFile = fileInput.files[0];

    if (!uploadedFile) {
        alert('Please select a file to upload');
        return;
    }

    const formData = new FormData();
    formData.append("file", uploadedFile);

    showLoadingSpinner();

    fetch('/upload', {
        method: 'POST',
        body: formData,
    })
    .then(response => response.json())
    .then(data => {
        document.querySelector('.upload').classList.add('success'); // Success message after upload
        hideLoadingSpinner();
    })
    .catch(error => {
        hideLoadingSpinner();
        alert('Error uploading file: ' + error.message);
    });
}

// Tab navigation logic
function openTab(event, tabName) {
    let i, tabcontent, tablinks;
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }
    tablinks = document.getElementsByClassName("tablinks");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].classList.remove("active");
    }
    document.getElementById(tabName).style.display = "block";
    event.currentTarget.classList.add("active");
}

// Ask question logic
function askQuestion() {
    const question = document.getElementById('user-question').value;
    showLoadingSpinner();

    fetch('/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question })
    })
    .then(response => response.json())
    .then(data => {
        hideLoadingSpinner();
        document.getElementById('chat-answer').innerHTML = `<b>Answer:</b> ${data.answer}`;
    })
    .catch(error => {
        hideLoadingSpinner();
        alert('Error asking question: ' + error.message);
    });
}

// Generate quiz logic
function generateQuiz() {
    const numQuestions = document.getElementById('num-questions').value;
    const difficulty = document.getElementById('difficulty').value;

    showLoadingSpinner();

    fetch('/generate_quiz', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ numQuestions, difficulty })
    })
    .then(response => response.json())
    .then(data => {
        hideLoadingSpinner();
        renderQuiz(data.quiz);
    })
    .catch(error => {
        hideLoadingSpinner();
        alert('Error generating quiz: ' + error.message);
    });
}

// Render quiz questions dynamically with buttons
function renderQuiz(quiz) {
    let quizHtml = "";
    quiz.forEach((question, index) => {
        quizHtml += `
            <div class="quiz-question" data-question-id="${index}">
                <b>Q${question.question}</b><br>
                ${Object.keys(question.options).map(key => {
                    return `<label onclick="selectOption(event, '${key}', ${index})">${question.options[key]}</label>`;
                }).join('')}
            </div>
        `;
    });
    document.getElementById('quiz-container').innerHTML = quizHtml;
    document.getElementById('submit-btn').style.display = "block";
}

// Select an option when clicked
function selectOption(event, optionKey, questionIndex) {
    // Store the selected option
    selectedAnswers[questionIndex] = optionKey;

    const labels = document.querySelectorAll(`#quiz-container .quiz-question:nth-child(${questionIndex + 1}) label`);
    
    // Remove 'selected' class from all labels
    labels.forEach(label => label.classList.remove('selected'));
    
    // Add 'selected' class to the clicked label
    event.target.classList.add('selected');
}

// Submit quiz logic
function submitQuiz() {
    if (Object.keys(selectedAnswers).length === 0) {
        alert("Please select at least one answer before submitting!");
        return;
    }

    // Prepare the quiz data to be sent to the server
    const quizData = [];
    for (let questionIndex in selectedAnswers) {
        quizData.push({
            questionIndex: questionIndex,
            answer: selectedAnswers[questionIndex]
        });
    }

    fetch('/submit_quiz', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ quizData })
    })
    .then(response => response.json())
    .then(data => {
        displayQuizResults(data);
    })
    .catch(error => {
        alert('Error submitting quiz: ' + error.message);
    });
}

// Display quiz results
function displayQuizResults(data) {
    const { score, total, correct_answers } = data;
    document.getElementById('quiz-result').innerHTML = `You scored ${score} out of ${total}`;

    let answersHtml = "<h3>Correct Answers:</h3>";
    correct_answers.forEach(answer => {
        answersHtml += `
            <div>
                <b>${answer.question}</b><br>
                Correct Answer: <b>${answer.correct_answer}</b><br>
                Your Answer: <b>${answer.selected_answer}</b><br>
                <hr>
            </div>
        `;
    });
    document.getElementById('quiz-result').innerHTML += answersHtml;
}
