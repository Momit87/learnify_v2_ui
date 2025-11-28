from flask import Flask, render_template, request, jsonify
from utils.file_parser import extract_text_from_pdf, extract_text_from_docx
from utils.quiz_generator import generate_quiz, parse_quiz_to_dict
from utils.gemini_rag import GeminiRAG

app = Flask(__name__)

# Initialize RAG
rag = GeminiRAG()
file_text = ""
quiz_data = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    global file_text
    file = request.files['file']
    if file.filename.endswith('.pdf'):
        file_text = extract_text_from_pdf(file)
    elif file.filename.endswith('.docx'):
        file_text = extract_text_from_docx(file)
    rag.build_index(file_text)
    return jsonify({"message": "File uploaded and processed successfully!"})

@app.route('/ask', methods=['POST'])
def ask_question():
    question = request.json.get('question')
    if file_text and question:
        answer = rag.ask(question)
        return jsonify({"answer": answer})
    return jsonify({"answer": "No document processed yet."})

@app.route('/generate_quiz', methods=['POST'])
def generate_quiz_route():
    global quiz_data
    data = request.json
    num_questions = int(data['numQuestions'])
    difficulty = data['difficulty']
    quiz_text = generate_quiz(file_text, num_questions, difficulty)
    quiz_data = parse_quiz_to_dict(quiz_text)  # Store quiz data for scoring
    return jsonify({"quiz": quiz_data})

@app.route('/submit_quiz', methods=['POST'])
def submit_quiz():
    data = request.json
    quiz_data_from_frontend = data['quizData']
    score = 0
    total = len(quiz_data)
    correct_answers = []

    print("Received quiz data:", quiz_data_from_frontend)  # Debugging line to check the structure
    print("Stored quiz data:", quiz_data)  # Debugging line to check the stored quiz data

    for i, q in enumerate(quiz_data):
        print(f"Question {i}: {q}")  # Debugging line to check individual question structure

        if 'question' in q and 'correct' in q:
            selected_answer = next((item for item in quiz_data_from_frontend if int(item["questionIndex"]) == i), None)
            
            if selected_answer and selected_answer["answer"] == q["correct"]:
                score += 1
                
            correct_answers.append({
                'question': q['question'],
                'correct_answer': q['correct'],
                'selected_answer': selected_answer["answer"] if selected_answer else "None"
            })
        else:
            print(f"Missing keys in question {i}: {q}")

    return jsonify({"score": score, "total": total, "correct_answers": correct_answers})

if __name__ == '__main__':
    app.run()
