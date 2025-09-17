import os
import tempfile
from flask import Flask, request, jsonify
from flask_cors import CORS
import fitz  # PyMuPDF
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import re
import requests
import json
import speech_recognition as sr
from pydub import AudioSegment
import traceback

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})

# Configuration
OLLAMA_MODEL = "ibm/granite3.3:2b"  # Matches your installed model
UPLOAD_FOLDER = tempfile.mkdtemp()
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize Embeddings
try:
    embeddings = SentenceTransformer('all-MiniLM-L6-v2')
except Exception as e:
    print(f"Embedding initialization failed: {str(e)}")

# Function to initialize Ollama
def initialize_ollama():
    try:
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code != 200:
            raise ValueError(f"Ollama server not running. Start it with 'ollama serve'. Response: {response.status_code} - {response.text}")
        models = json.loads(response.text).get("models", [])
        model_names = [m["name"] for m in models]
        if OLLAMA_MODEL not in model_names:
            raise ValueError(f"Model '{OLLAMA_MODEL}' not found. Available models: {model_names}. Pull the model with 'ollama pull {OLLAMA_MODEL}'.")
        return True
    except Exception as e:
        raise ValueError(f"Failed to initialize Ollama: {str(e)}")

# Function to extract text from PDFs
def extract_text_from_pdf(file_path):
    try:
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    except Exception as e:
        raise ValueError(f"Error extracting text from PDF: {str(e)}")

# Function to transcribe audio
def transcribe_audio(file_path):
    try:
        audio = AudioSegment.from_file(file_path)
        wav_path = os.path.join(app.config['UPLOAD_FOLDER'], "temp_audio.wav")
        audio.export(wav_path, format="wav")
        
        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)
        
        os.remove(wav_path)  # Clean up temporary file
        return text
    except Exception as e:
        raise ValueError(f"Error transcribing audio: {str(e)}")

# Function to clean text
def clean_text(text):
    text = re.sub(r'\s+', ' ', text.strip())
    return text

# Function to chunk text
def chunk_text(text, chunk_size=500, overlap=100):
    if not text:
        return []
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
    return chunks

# Function to create FAISS index
def create_faiss_index(chunks):
    if not chunks:
        raise ValueError("No text chunks available to index")
    try:
        embedder = embeddings
        embeddings_array = embedder.encode(chunks, convert_to_numpy=True, show_progress_bar=False)
        dimension = embeddings_array.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings_array)
        return index, chunks
    except Exception as e:
        raise ValueError(f"Error creating FAISS index: {str(e)}")

# Function to retrieve top-k chunks
def retrieve_chunks(query, index, chunks, k=3):
    if index is None or not chunks:
        return []
    try:
        query_embedding = embeddings.encode([query], convert_to_numpy=True)
        distances, indices = index.search(query_embedding, min(k, len(chunks)))
        return [chunks[i] for i in indices[0] if i < len(chunks)]
    except Exception as e:
        raise ValueError(f"Error retrieving chunks: {str(e)}")

# Function to construct prompt for RAG
def construct_prompt(query, retrieved_chunks):
    context = "\n\n".join(retrieved_chunks) if retrieved_chunks else "No relevant context found."
    prompt = f"""You are an assistant helping a user understand content from a knowledge base built from uploaded PDFs or audio transcripts. Based on the following context, provide a concise and accurate answer to the user's question. If the context doesn't contain enough information, say so and provide a general response if applicable.

**Context:**
{context}

**Question:**
{query}

**Answer:**
"""
    return prompt

# Function to get LLM response from Ollama
def get_llm_response(prompt):
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "top_p": 0.9,
                    "num_predict": 300
                }
            }
        )
        if response.status_code == 200:
            return json.loads(response.text).get("response", "").strip()
        else:
            raise ValueError(f"Ollama API returned status {response.status_code}: {response.text}")
    except Exception as e:
        raise ValueError(f"Error during generation: {str(e)}")

@app.route('/api/answer-question', methods=['POST'])
def answer_question():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    question = request.form.get('question')
    if not question:
        return jsonify({"error": "No question provided"}), 400

    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    if not (file.filename.lower().endswith('.pdf') or file.filename.lower().endswith(('.mp3', '.wav'))):
        return jsonify({"error": "Please upload a valid PDF or audio file (MP3, WAV)"}), 400

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    try:
        # Initialize Ollama
        initialize_ollama()

        # Save file
        file.save(file_path)

        # Process file based on type
        if file.filename.lower().endswith('.pdf'):
            text = extract_text_from_pdf(file_path)
        else:  # Audio file
            text = transcribe_audio(file_path)

        if not text:
            return jsonify({"error": "No text extracted from file"}), 400

        # Build knowledge base
        cleaned_text = clean_text(text)
        chunks = chunk_text(cleaned_text)
        if not chunks:
            return jsonify({"error": "No text chunks created from file"}), 400

        index, chunks = create_faiss_index(chunks)
        if index is None:
            return jsonify({"error": "Failed to build knowledge base index"}), 500

        # Retrieve relevant chunks and generate answer
        retrieved_chunks = retrieve_chunks(question, index, chunks)
        prompt = construct_prompt(question, retrieved_chunks)
        answer = get_llm_response(prompt)

        return jsonify({
            "message": "Answer generated successfully",
            "question": question,
            "answer": answer
        })

    except Exception as e:
        error_details = traceback.format_exc()
        return jsonify({"error": str(e), "details": error_details}), 500
    finally:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Failed to remove temporary file: {str(e)}")

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)