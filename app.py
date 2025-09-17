import streamlit as st
try:
    import fitz  # PyMuPDF
except ImportError:
    st.error("PyMuPDF is not installed. Please install it using `pip install pymupdf`.")
    st.stop()
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import re
try:
    from ollama import Client
except ImportError:
    st.error("Ollama Python client is not installed. Please install it using `pip install ollama`.")
    st.stop()
import pickle
import os

# ---------------------------
# Initialize Streamlit session state
# ---------------------------
if "qa_history" not in st.session_state:
    st.session_state.qa_history = []
if "chunks" not in st.session_state:
    st.session_state.chunks = []
if "index" not in st.session_state:
    st.session_state.index = None
if "embedder" not in st.session_state:
    st.session_state.embedder = SentenceTransformer('all-MiniLM-L6-v2')
if "ollama_client" not in st.session_state:
    st.session_state.ollama_client = None
if "pdf_files" not in st.session_state:
    st.session_state.pdf_files = []  # Track uploaded PDF filenames

# ---------------------------
# Persistent storage paths
# ---------------------------
INDEX_FILE = "faiss_index.bin"
CHUNKS_FILE = "chunks.pkl"
PDF_FILES_FILE = "pdf_files.pkl"

# ---------------------------
# Initialize Ollama Client
# ---------------------------
@st.cache_resource(show_spinner=True)
def initialize_ollama_client():
    MODEL_NAME = "granite3.3:2b"
    try:
        client = Client(host='http://localhost:11434')  # Default Ollama host
        # Test the client with a simple request
        client.generate(model=MODEL_NAME, prompt="Test", options={"num_predict": 10})
        st.info("Ollama client initialized successfully.")
        return client
    except Exception as e:
        st.error(f"Failed to initialize Ollama client: {str(e)}")
        st.error("Ensure Ollama is running and the granite3.3:2b model is pulled (`ollama pull granite3.3:2b`).")
        return None

if st.session_state.ollama_client is None:
    st.session_state.ollama_client = initialize_ollama_client()

# ---------------------------
# Load saved embeddings and chunks
# ---------------------------
@st.cache_resource(show_spinner=True)
def load_saved_embeddings():
    try:
        if os.path.exists(INDEX_FILE) and os.path.exists(CHUNKS_FILE) and os.path.exists(PDF_FILES_FILE):
            index = faiss.read_index(INDEX_FILE)
            with open(CHUNKS_FILE, 'rb') as f:
                chunks = pickle.load(f)
            with open(PDF_FILES_FILE, 'rb') as f:
                pdf_files = pickle.load(f)
            st.session_state.chunks = chunks
            st.session_state.pdf_files = pdf_files
            return index
        return None
    except Exception as e:
        st.error(f"Failed to load saved embeddings: {str(e)}")
        return None

# ---------------------------
# Save embeddings and chunks
# ---------------------------
def save_embeddings(index, chunks, pdf_files):
    try:
        faiss.write_index(index, INDEX_FILE)
        with open(CHUNKS_FILE, 'wb') as f:
            pickle.dump(chunks, f)
        with open(PDF_FILES_FILE, 'wb') as f:
            pickle.dump(pdf_files, f)
        st.success("Embeddings and chunks saved successfully.")
    except Exception as e:
        st.error(f"Failed to save embeddings: {str(e)}")

# ---------------------------
# PDF processing functions
# ---------------------------
def extract_text_from_pdf(pdf_file):
    try:
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    except Exception as e:
        st.error(f"Error processing PDF {pdf_file.name}: {str(e)}")
        return ""

def clean_text(text):
    return re.sub(r'\s+', ' ', text.strip())

def chunk_text(text, chunk_size=500, overlap=100):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
    return chunks

# ---------------------------
# FAISS index functions
# ---------------------------
def create_faiss_index(chunks):
    try:
        embedder = st.session_state.embedder
        embeddings = embedder.encode(chunks, convert_to_numpy=True)
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings)
        return index, embeddings
    except Exception as e:
        st.error(f"Error creating FAISS index: {str(e)}")
        return None, None

def retrieve_chunks(query, index, chunks, k=3):
    try:
        embedder = st.session_state.embedder
        query_embedding = embedder.encode([query], convert_to_numpy=True)
        distances, indices = index.search(query_embedding, k)
        return [chunks[i] for i in indices[0]]
    except Exception as e:
        st.error(f"Error retrieving chunks: {str(e)}")
        return []

# ---------------------------
# Prompt construction
# ---------------------------
def construct_prompt(query, retrieved_chunks):
    context = "\n\n".join(retrieved_chunks)
    prompt = f"""You are an assistant helping a user understand content from uploaded PDFs. Based on the following context from multiple PDFs, provide a concise and accurate answer to the user's question. If the context doesn't contain enough information, say so.
*Context:*
{context}
*Question:*
{query}
*Answer:*
"""
    return prompt

# ---------------------------
# LLM response via Ollama
# ---------------------------
def get_llm_response(prompt):
    try:
        if st.session_state.ollama_client is None:
            return "Error: Ollama client not initialized."
        response = st.session_state.ollama_client.generate(
            model="granite3.3:2b",
            prompt=prompt,
            options={
                "num_predict": 256,  # Equivalent to max_new_tokens
                "temperature": 0.7,
                "top_p": 1.0  # Matches do_sample=True behavior
            }
        )
        # Extract the answer part after "*Answer:*"
        answer_start = response['response'].find("*Answer:*") + len("*Answer:*")
        return response['response'][answer_start:].strip() if answer_start > len("*Answer:*") else response['response']
    except Exception as e:
        return f"Error: {str(e)}"

# ---------------------------
# Export Q&A log
# ---------------------------
def export_qa_log():
    log = "\n\n".join([f"Q: {qa['question']}\nA: {qa['answer']}\nSource Chunks:\n{qa['source']}" for qa in st.session_state.qa_history])
    return log

# ---------------------------
# Streamlit UI
# ---------------------------
st.title("StudyMate: PDF Q&A (Granite-3.3-2B via Ollama)")
st.write("Upload one or more PDFs to embed their content. Questions will be answered using context from all uploaded PDFs. Embeddings are saved for reuse across sessions.")

# Load saved embeddings on startup
if st.session_state.index is None:
    st.session_state.index = load_saved_embeddings()

# PDF Upload
uploaded_files = st.file_uploader("Upload PDF files", type="pdf", accept_multiple_files=True)
if uploaded_files:
    all_text = ""
    new_pdf_files = [f.name for f in uploaded_files]
    # Check if new PDFs differ from previously processed ones
    if set(new_pdf_files) != set(st.session_state.pdf_files):
        st.session_state.pdf_files.extend(new_pdf_files)
        for pdf_file in uploaded_files:
            text = extract_text_from_pdf(pdf_file)
            if text:
                all_text += text + " "
        
        if all_text:
            cleaned_text = clean_text(all_text)
            new_chunks = chunk_text(cleaned_text)
            # Combine new chunks with existing ones
            st.session_state.chunks.extend(new_chunks)
            st.session_state.index, _ = create_faiss_index(st.session_state.chunks)
            if st.session_state.index:
                st.success("PDFs processed and indexed successfully!")
                save_embeddings(st.session_state.index, st.session_state.chunks, st.session_state.pdf_files)
            else:
                st.error("Failed to create FAISS index. Please check the logs.")
        else:
            st.error("No text extracted from PDFs.")
    else:
        st.info("Uploaded PDFs already processed. Using existing embeddings.")

# Query Input
query = st.text_input("Ask a question about the PDFs:")
if query and st.session_state.index:
    retrieved_chunks = retrieve_chunks(query, st.session_state.index, st.session_state.chunks)
    if retrieved_chunks:
        prompt = construct_prompt(query, retrieved_chunks)
        answer = get_llm_response(prompt)
        
        st.session_state.qa_history.append({
            "question": query,
            "answer": answer,
            "source": "\n".join(retrieved_chunks)
        })
        
        st.write("*Answer:*")
        st.write(answer)
    else:
        st.error("No relevant chunks retrieved for the query.")

# Display Q&A History
if st.session_state.qa_history:
    st.subheader("Q&A History")
    for i, qa in enumerate(st.session_state.qa_history):
        st.write(f"*Q{i+1}:* {qa['question']}")
        st.write(f"*A{i+1}:* {qa['answer']}")
        st.write("*Source:*")
        st.write(qa['source'])
        st.write("---")

# Download Q&A log
if st.session_state.qa_history:
    log = export_qa_log()
    st.download_button(
        label="Download Q&A Log",
        data=log,
        file_name="qa_log.txt",
        mime="text/plain"
    )

# Clear Embeddings Button
if st.button("Clear Stored Embeddings"):
    st.session_state.chunks = []
    st.session_state.index = None
    st.session_state.pdf_files = []
    for file in [INDEX_FILE, CHUNKS_FILE, PDF_FILES_FILE]:
        if os.path.exists(file):
            os.remove(file)
    st.success("Stored embeddings cleared. Upload new PDFs to start fresh.")