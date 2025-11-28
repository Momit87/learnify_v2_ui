import os
from dotenv import load_dotenv
import google.generativeai as genai
import re

# Load Gemini
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

def generate_quiz(text, num_questions=5, difficulty="medium"):
    prompt = f"""
You are a quiz generator AI.

Create {num_questions} multiple-choice questions (MCQs) from the following passage.
Difficulty: {difficulty}.
Return in this format:

Q1: [Question]
A. [Option]
B. [Option]
C. [Option]
D. [Option]
Answer: [Correct Option]

Text:
{text[:2000]}
"""

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠️ Error generating quiz: {e}"

def parse_quiz_to_dict(quiz_text):
    questions = []
    blocks = quiz_text.strip().split("Q")
    for block in blocks[1:]:
        lines = block.strip().split("\n")
        question_line = lines[0]
        options = {line[0]: line[3:].strip() for line in lines[1:5] if line[0] in "ABCD"}
        answer_line = next((l for l in lines if l.lower().startswith("answer")), "")
        correct = answer_line.split(":")[-1].strip().upper()
        questions.append({
            "question": question_line.strip(),
            "options": options,
            "correct": correct
        })
    return questions
