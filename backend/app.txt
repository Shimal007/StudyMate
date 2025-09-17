import os
import tempfile
from flask import Flask, request, jsonify  # Corrected import
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
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Allow all origins for development

# Configuration
OLLAMA_MODEL = "ibm/granite3.3:2b"  # Matches your installed model
UPLOAD_FOLDER = tempfile.mkdtemp()
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024  # 200MB max file size

# Initialize Embeddings
embeddings = None
try:
    embeddings = SentenceTransformer('all-MiniLM-L6-v2')
    logger.info("✅ Sentence Transformers initialized successfully")
except Exception as e:
    logger.error(f"❌ Embedding initialization failed: {str(e)}")

# Store processed documents in memory (for better persistence, use a database)
document_store = {}

@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "message": "StudyMate Flask API is running",
        "timestamp": datetime.now().isoformat()
    })

def initialize_ollama():
    """Initialize and check Ollama connection"""
    try:
        logger.info("🔄 Checking Ollama connection...")
        response = requests.get("http://localhost:11434/api/tags", timeout=10)
        
        if response.status_code != 200:
            error_msg = f"Ollama server not responding. Status: {response.status_code}"
            logger.error(f"❌ {error_msg}")
            raise ValueError(error_msg)
            
        models_data = response.json()
        models = models_data.get("models", [])
        model_names = [m["name"] for m in models]
        
        logger.info(f"📋 Available models: {model_names}")
        
        if OLLAMA_MODEL not in model_names:
            error_msg = f"Model '{OLLAMA_MODEL}' not found. Available: {model_names}"
            logger.error(f"❌ {error_msg}")
            raise ValueError(error_msg)
            
        logger.info(f"✅ Ollama initialized successfully with model: {OLLAMA_MODEL}")
        return True
        
    except requests.exceptions.ConnectionError:
        error_msg = "Cannot connect to Ollama server. Please start it with 'ollama serve'"
        logger.error(f"❌ {error_msg}")
        raise ValueError(error_msg)
    except Exception as e:
        error_msg = f"Failed to initialize Ollama: {str(e)}"
        logger.error(f"❌ {error_msg}")
        raise ValueError(error_msg)

def extract_text_from_pdf(file_path):
    """Extract text from PDF with better error handling"""
    try:
        logger.info(f"📄 Extracting text from PDF: {file_path}")
        doc = fitz.open(file_path)
        text = ""
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            page_text = page.get_text()
            text += f"\n--- Page {page_num + 1} ---\n{page_text}"
            
        doc.close()
        
        logger.info(f"✅ Extracted {len(text)} characters from PDF")
        return text
        
    except Exception as e:
        error_msg = f"Error extracting text from PDF: {str(e)}"
        logger.error(f"❌ {error_msg}")
        raise ValueError(error_msg)

def transcribe_audio(file_path):
    """Transcribe audio with better error handling"""
    try:
        logger.info(f"🎵 Transcribing audio: {file_path}")
        
        # Convert to WAV format
        audio = AudioSegment.from_file(file_path)
        wav_path = os.path.join(app.config['UPLOAD_FOLDER'], f"temp_audio_{datetime.now().timestamp()}.wav")
        
        # Normalize audio for better recognition
        audio = audio.normalize()
        audio.export(wav_path, format="wav")
        
        # Transcribe
        recognizer = sr.Recognizer()
        recognizer.energy_threshold = 300
        recognizer.dynamic_energy_threshold = True
        
        with sr.AudioFile(wav_path) as source:
            # Adjust for ambient noise
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio_data = recognizer.record(source)
            
            # Try different recognition engines
            try:
                text = recognizer.recognize_google(audio_data)
                logger.info(f"✅ Google Speech Recognition successful")
            except sr.UnknownValueError:
                logger.warning("⚠️ Google Speech Recognition could not understand audio")
                try:
                    text = recognizer.recognize_sphinx(audio_data)
                    logger.info("✅ Sphinx Recognition successful")
                except:
                    raise ValueError("Could not transcribe audio - speech unclear or no speech detected")
            except sr.RequestError as e:
                logger.error(f"❌ Speech Recognition service error: {e}")
                raise ValueError(f"Speech Recognition service error: {e}")
        
        # Clean up temporary file
        if os.path.exists(wav_path):
            os.remove(wav_path)
            
        logger.info(f"✅ Transcribed {len(text)} characters from audio")
        return text
        
    except Exception as e:
        error_msg = f"Error transcribing audio: {str(e)}"
        logger.error(f"❌ {error_msg}")
        raise ValueError(error_msg)

def clean_text(text):
    """Clean and normalize text"""
    if not text:
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove special characters but keep punctuation
    text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)]', ' ', text)
    
    # Remove page markers from PDF
    text = re.sub(r'--- Page \d+ ---', '', text)
    
    return text

def chunk_text(text, chunk_size=300, overlap=50):
    """Create overlapping chunks for better context preservation"""
    if not text:
        return []
    
    # Split by sentences first
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        # If adding this sentence would exceed chunk size, save current chunk
        if len(current_chunk.split()) + len(sentence.split()) > chunk_size and current_chunk:
            chunks.append(current_chunk.strip())
            
            # Start new chunk with overlap
            words = current_chunk.split()
            if len(words) > overlap:
                current_chunk = " ".join(words[-overlap:]) + " " + sentence
            else:
                current_chunk = sentence
        else:
            current_chunk += " " + sentence if current_chunk else sentence
    
    # Add the last chunk
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    logger.info(f"✅ Created {len(chunks)} text chunks")
    return chunks

def create_faiss_index(chunks):
    """Create FAISS index with error handling"""
    if not chunks:
        raise ValueError("No text chunks available to index")
    
    try:
        logger.info(f"🔄 Creating FAISS index for {len(chunks)} chunks...")
        
        if embeddings is None:
            raise ValueError("Embeddings model not initialized")
        
        # Generate embeddings
        embeddings_array = embeddings.encode(
            chunks, 
            convert_to_numpy=True, 
            show_progress_bar=False,
            batch_size=32
        )
        
        # Create FAISS index
        dimension = embeddings_array.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings_array.astype('float32'))
        
        logger.info(f"✅ FAISS index created successfully with {index.ntotal} vectors")
        return index, chunks
        
    except Exception as e:
        error_msg = f"Error creating FAISS index: {str(e)}"
        logger.error(f"❌ {error_msg}")
        raise ValueError(error_msg)

def retrieve_chunks(query, index, chunks, k=5):
    """Retrieve most relevant chunks with better scoring"""
    if index is None or not chunks:
        logger.warning("⚠️ No index or chunks available for retrieval")
        return []
    
    try:
        logger.info(f"🔍 Searching for relevant chunks for query: '{query[:50]}...'")
        
        # Generate query embedding
        query_embedding = embeddings.encode([query], convert_to_numpy=True)
        
        # Search for similar chunks
        k = min(k, len(chunks))  # Don't search for more chunks than available
        distances, indices = index.search(query_embedding.astype('float32'), k)
        
        # Get chunks with their similarity scores
        retrieved_chunks = []
        for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
            if idx < len(chunks):
                similarity_score = 1 / (1 + distance)  # Convert distance to similarity
                retrieved_chunks.append({
                    'text': chunks[idx],
                    'score': similarity_score,
                    'rank': i + 1
                })
        
        # Sort by similarity score (higher is better)
        retrieved_chunks.sort(key=lambda x: x['score'], reverse=True)
        
        logger.info(f"✅ Retrieved {len(retrieved_chunks)} relevant chunks")
        return [chunk['text'] for chunk in retrieved_chunks]
        
    except Exception as e:
        error_msg = f"Error retrieving chunks: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return []

def construct_prompt(query, retrieved_chunks):
    """Construct a better prompt for RAG"""
    if retrieved_chunks:
        context = "\n\n".join([f"[Context {i+1}]: {chunk}" for i, chunk in enumerate(retrieved_chunks)])
    else:
        context = "No relevant context found in the uploaded document."
    
    prompt = f"""You are StudyMate, an intelligent assistant that helps users understand and learn from their uploaded documents. 

Based on the following context from the user's document, provide a comprehensive and accurate answer to their question. If the context doesn't contain enough information, clearly state what information is missing and provide any relevant general knowledge that might help.

CONTEXT FROM DOCUMENT:
{context}

USER QUESTION: {query}

INSTRUCTIONS:
1. Answer based primarily on the provided context
2. Be specific and detailed in your response
3. If the context is insufficient, explain what's missing
4. Use clear, educational language
5. Organize your answer with bullet points or sections if helpful
6. If you find contradictory information, mention it

ANSWER:"""
    
    return prompt

def get_llm_response(prompt):
    """Get response from Ollama with better error handling and parameters"""
    try:
        logger.info("🤖 Generating response from Ollama...")
        
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,  # Slightly higher for more natural responses
                    "top_p": 0.85,
                    "top_k": 40,
                    "num_predict": 500,  # Allow longer responses
                    "repeat_penalty": 1.1,
                    "num_ctx": 4096  # Larger context window
                }
            },
            timeout=180  # 3 minute timeout
        )
        
        if response.status_code == 200:
            result = response.json()
            answer = result.get("response", "").strip()
            
            if not answer:
                logger.warning("⚠️ Empty response from Ollama")
                return "I apologize, but I couldn't generate a proper response. Please try rephrasing your question."
            
            logger.info(f"✅ Generated response of {len(answer)} characters")
            return answer
        else:
            error_msg = f"Ollama API error: Status {response.status_code} - {response.text}"
            logger.error(f"❌ {error_msg}")
            raise ValueError(error_msg)
            
    except requests.exceptions.Timeout:
        error_msg = "Request to Ollama timed out. The model might be processing a complex query."
        logger.error(f"❌ {error_msg}")
        raise ValueError(error_msg)
    except Exception as e:
        error_msg = f"Error during response generation: {str(e)}"
        logger.error(f"❌ {error_msg}")
        raise ValueError(error_msg)

@app.route('/api/answer-question', methods=['POST'])
def answer_question():
    """Main endpoint for answering questions about uploaded documents"""
    request_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    logger.info(f"🚀 New request [{request_id}] received")
    
    try:
        # Validate request
        if 'file' not in request.files:
            logger.warning(f"❌ [{request_id}] No file uploaded")
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files['file']
        question = request.form.get('question', '').strip()
        
        if not question:
            logger.warning(f"❌ [{request_id}] No question provided")
            return jsonify({"error": "No question provided"}), 400

        if file.filename == '':
            logger.warning(f"❌ [{request_id}] No file selected")
            return jsonify({"error": "No file selected"}), 400

        # Validate file type
        allowed_extensions = ('.pdf', '.mp3', '.wav')
        if not file.filename.lower().endswith(allowed_extensions):
            logger.warning(f"❌ [{request_id}] Invalid file type: {file.filename}")
            return jsonify({"error": "Please upload a valid PDF or audio file (MP3, WAV)"}), 400

        logger.info(f"📁 [{request_id}] Processing file: {file.filename}, Question: {question[:100]}...")

        # Initialize Ollama
        initialize_ollama()

        # Save file temporarily
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{request_id}_{file.filename}")
        file.save(file_path)
        
        try:
            # Process file based on type
            if file.filename.lower().endswith('.pdf'):
                logger.info(f"📄 [{request_id}] Processing PDF file...")
                text = extract_text_from_pdf(file_path)
            else:  # Audio file
                logger.info(f"🎵 [{request_id}] Processing audio file...")
                text = transcribe_audio(file_path)

            if not text or len(text.strip()) < 10:
                logger.warning(f"❌ [{request_id}] No meaningful text extracted")
                return jsonify({"error": "No meaningful text could be extracted from the file"}), 400

            # Build knowledge base
            logger.info(f"🔄 [{request_id}] Building knowledge base...")
            cleaned_text = clean_text(text)
            chunks = chunk_text(cleaned_text)
            
            if not chunks:
                logger.warning(f"❌ [{request_id}] No text chunks created")
                return jsonify({"error": "Could not create text chunks from the file"}), 400

            # Create search index
            index, chunks = create_faiss_index(chunks)
            
            # Store document for potential future use
            document_store[request_id] = {
                'filename': file.filename,
                'chunks': chunks,
                'index': index,
                'timestamp': datetime.now().isoformat()
            }

            # Retrieve relevant chunks and generate answer
            logger.info(f"🔍 [{request_id}] Retrieving relevant information...")
            retrieved_chunks = retrieve_chunks(question, index, chunks)
            
            logger.info(f"🤖 [{request_id}] Generating answer...")
            prompt = construct_prompt(question, retrieved_chunks)
            answer = get_llm_response(prompt)

            # Prepare response
            response_data = {
                "message": "Answer generated successfully",
                "request_id": request_id,
                "filename": file.filename,
                "question": question,
                "answer": answer,
                "chunks_used": len(retrieved_chunks),
                "total_chunks": len(chunks)
            }

            logger.info(f"✅ [{request_id}] Request completed successfully")
            return jsonify(response_data)

        finally:
            # Clean up temporary file
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    logger.info(f"🗑️ [{request_id}] Temporary file cleaned up")
                except Exception as e:
                    logger.warning(f"⚠️ [{request_id}] Failed to remove temporary file: {e}")

    except Exception as e:
        error_details = traceback.format_exc()
        logger.error(f"❌ [{request_id}] Unexpected error: {str(e)}\n{error_details}")
        
        return jsonify({
            "error": str(e),
            "request_id": request_id,
            "details": "Check server logs for more information"
        }), 500

@app.route('/api/health', methods=['GET'])
def detailed_health_check():
    """Detailed health check for debugging"""
    health_status = {
        "timestamp": datetime.now().isoformat(),
        "flask_server": "running",
        "embeddings_model": "loaded" if embeddings else "failed",
        "ollama_connection": "unknown",
        "document_store_count": len(document_store)
    }
    
    # Check Ollama connection
    try:
        initialize_ollama()
        health_status["ollama_connection"] = "connected"
        health_status["ollama_model"] = OLLAMA_MODEL
    except Exception as e:
        health_status["ollama_connection"] = f"failed: {str(e)}"
    
    return jsonify(health_status)

if __name__ == "__main__":
    logger.info("🚀 Starting StudyMate Flask API...")
    logger.info(f"📁 Upload folder: {UPLOAD_FOLDER}")
    logger.info(f"🤖 Ollama model: {OLLAMA_MODEL}")
    
    app.run(debug=True, host='0.0.0.0', port=5000)