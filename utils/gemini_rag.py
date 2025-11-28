import os
import faiss
import numpy as np
import re
from dotenv import load_dotenv
import google.generativeai as genai
from sentence_transformers import SentenceTransformer

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Load Gemini model
model = genai.GenerativeModel("gemini-2.5-flash")

# Load embedding model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

class GeminiRAG:
    def __init__(self):
        self.index = None
        self.text_chunks = []

    def _clean_text(self, text):
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def chunk_text(self, text, max_words=120):
        words = self._clean_text(text).split()
        chunks = []
        for i in range(0, len(words), max_words):
            chunk = " ".join(words[i:i+max_words])
            chunks.append(chunk)
        return chunks

    def build_index(self, text):
        self.text_chunks = self.chunk_text(text)
        embeddings = embedding_model.encode(self.text_chunks)
        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dim)
        self.index.add(np.array(embeddings))

    def retrieve_chunks(self, query, top_k=3):
        query_vec = embedding_model.encode([query])
        distances, indices = self.index.search(np.array(query_vec), top_k)
        return "\n".join([self.text_chunks[i] for i in indices[0]])

    def ask(self, query, top_k=3):
        context = self.retrieve_chunks(query, top_k)
        prompt = f"""Use the following context to answer the question.

Context:
{context}

Question:
{query}
"""
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"❌ Error: {e}"
