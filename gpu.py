import streamlit as st
import requests
import time
from datetime import datetime
import tempfile
import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import io

# Page configuration
st.set_page_config(
    page_title="StudyMate - Study Center",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for attractive styling
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Main app styling */
    .stApp {
        background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
        font-family: 'Inter', sans-serif;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #1e1e2e 0%, #2a2a3e 100%);
        border-right: 1px solid rgba(99, 102, 241, 0.2);
    }
    
    /* Main content area */
    .main .block-container {
        padding: 2rem 3rem;
        background: rgba(255, 255, 255, 0.02);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        margin: 1rem;
        border: 1px solid rgba(99, 102, 241, 0.1);
    }
    
    /* Custom title styling */
    .main-title {
        background: linear-gradient(135deg, #6366f1, #a855f7, #06b6d4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 0 0 30px rgba(99, 102, 241, 0.3);
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
        background: rgba(30, 30, 46, 0.5);
        padding: 10px;
        border-radius: 15px;
        border: 1px solid rgba(99, 102, 241, 0.2);
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(99, 102, 241, 0.1);
        border-radius: 10px;
        color: #ffffff;
        border: 1px solid rgba(99, 102, 241, 0.2);
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #6366f1, #a855f7);
        box-shadow: 0 5px 15px rgba(99, 102, 241, 0.4);
    }
    
    /* File uploader styling */
    .uploadedFile {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(168, 85, 247, 0.1));
        border: 2px dashed rgba(99, 102, 241, 0.3);
        border-radius: 15px;
        padding: 2rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #6366f1, #a855f7);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 5px 15px rgba(99, 102, 241, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.5);
    }
    
    /* Success message styling */
    .success-message {
        background: linear-gradient(135deg, #10b981, #059669);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 5px 15px rgba(16, 185, 129, 0.3);
    }
    
    /* Card styling */
    .study-card {
        background: rgba(30, 30, 46, 0.8);
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    
    .study-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(99, 102, 241, 0.2);
        border-color: rgba(99, 102, 241, 0.4);
    }
    
    /* Answer box styling */
    .answer-box {
        background: rgba(16, 185, 129, 0.1);
        border: 1px solid rgba(16, 185, 129, 0.3);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        color: #ffffff;
    }
    
    .question-box {
        background: rgba(99, 102, 241, 0.1);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 15px;
        padding: 1rem;
        margin: 1rem 0;
        color: #ffffff;
    }
    
    /* Sidebar menu styling */
    .sidebar-menu {
        background: rgba(30, 30, 46, 0.8);
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        border: 1px solid rgba(99, 102, 241, 0.2);
        transition: all 0.3s ease;
    }
    
    .sidebar-menu:hover {
        background: rgba(99, 102, 241, 0.1);
        transform: translateX(5px);
    }
    
    /* Progress bar styling */
    .stProgress > div > div > div > div {
        background: linear-gradient(135deg, #6366f1, #a855f7);
    }
    
    /* Text input styling */
    .stTextInput > div > div > input {
        background: rgba(30, 30, 46, 0.8);
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 10px;
        color: white;
    }
    
    /* File uploader drag and drop area */
    .stFileUploader > label > div {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(168, 85, 247, 0.1));
        border: 2px dashed rgba(99, 102, 241, 0.3);
        border-radius: 15px;
        transition: all 0.3s ease;
    }
    
    .stFileUploader > label > div:hover {
        border-color: rgba(99, 102, 241, 0.5);
        background: rgba(99, 102, 241, 0.15);
    }
    
    /* Metric cards */
    [data-testid="metric-container"] {
        background: rgba(30, 30, 46, 0.8);
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 15px;
        padding: 1rem;
        backdrop-filter: blur(10px);
    }
    
    /* Download button styling */
    .download-btn {
        background: linear-gradient(135deg, #059669, #10b981) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.5rem 1rem !important;
        font-weight: 600 !important;
        margin-top: 1rem !important;
    }
</style>
""", unsafe_allow_html=True)

# Configuration
FLASK_API_URL = "http://localhost:5000/api/answer-question"

# Initialize session state
if 'processed_sources' not in st.session_state:
    st.session_state.processed_sources = []
if 'study_progress' not in st.session_state:
    st.session_state.study_progress = 0
if 'qa_history' not in st.session_state:
    st.session_state.qa_history = []

# Function to call Flask API
def call_flask_api(source=None, youtube_url=None, question=None):
    """Call the Flask API to get answer for the question"""
    try:
        data = {'question': question}
        files = None
        if youtube_url:
            data['youtube_url'] = youtube_url
        elif source:
            files = {'file': (source.name, source.getvalue(), source.type)}
        
        response = requests.post(FLASK_API_URL, files=files, data=data, timeout=120)
        
        if response.status_code == 200:
            return response.json()
        else:
            error_data = response.json() if response.headers.get('content-type') == 'application/json' else {"error": response.text}
            return {"error": f"API Error: {error_data.get('error', 'Unknown error')}"}
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to Flask server. Please ensure it's running on http://localhost:5000"}
    except requests.exceptions.Timeout:
        return {"error": "Request timed out. The file or video might be too large or processing is taking too long."}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

# Function to create PDF from Q&A history
def create_qa_pdf(qa_history):
    """Create a PDF document from Q&A history"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=1*inch, bottomMargin=1*inch)
    
    # Get styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        textColor='#1f2937',
        alignment=1  # Center alignment
    )
    
    question_style = ParagraphStyle(
        'QuestionStyle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor='#3b82f6',
        spaceAfter=12,
        spaceBefore=20
    )
    
    answer_style = ParagraphStyle(
        'AnswerStyle',
        parent=styles['Normal'],
        fontSize=11,
        textColor='#374151',
        spaceAfter=20,
        leftIndent=20
    )
    
    # Build content
    content = []
    
    # Title
    content.append(Paragraph("StudyMate - Q&A Session Report", title_style))
    content.append(Spacer(1, 20))
    
    # Metadata
    content.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    content.append(Paragraph(f"Total Questions: {len(qa_history)}", styles['Normal']))
    content.append(Spacer(1, 30))
    
    # Q&A Content
    for i, qa in enumerate(qa_history, 1):
        content.append(Paragraph(f"Q{i}: {qa['question']}", question_style))
        content.append(Paragraph(f"Answer: {qa['answer']}", answer_style))
        content.append(Spacer(1, 10))
    
    # Build PDF
    doc.build(content)
    buffer.seek(0)
    return buffer

# Sidebar
with st.sidebar:
    st.markdown("<h1 style='color: #6366f1; text-align: center;'>🎓 StudyMate</h1>", unsafe_allow_html=True)
    
    # API Status Check
    try:
        status_response = requests.get("http://localhost:5000", timeout=5)
        st.success("✅ Flask Server Connected")
    except:
        st.error("❌ Flask Server Disconnected")
        st.info("Please start the Flask server:\n```bash\npython app.py\n```")
    
    # Navigation Menu
    st.markdown("### Navigation")
    
    menu_items = [
        ("🏠 Home", "home"),
        ("📚 Study", "study"),
        ("📝 Attend Test", "test"),
        ("📊 Progress", "progress"),
        ("⚙️ Settings", "settings")
    ]
    
    selected_page = st.radio("", [item[0] for item in menu_items], label_visibility="collapsed")
    
    st.markdown("---")
    
    # Study Modules
    st.markdown("### Study Modules")
    
    modules = [
        ("📄 PDF Study", "pdf_study"),
        ("🎵 Audio Study", "audio_study"),
        ("🎬 Video Study", "video_study")
    ]
    
    for module_name, module_key in modules:
        st.markdown(f'<div class="sidebar-menu">{module_name}</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Quick Stats
    st.markdown("### Quick Stats")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Sources Processed", len(st.session_state.processed_sources))
    with col2:
        st.metric("Questions Asked", len(st.session_state.qa_history))

# Main Content Area
st.markdown('<h1 class="main-title">📚 Study Center</h1>', unsafe_allow_html=True)

# Study Mode Tabs
tab1, tab2, tab3 = st.tabs(["📄 PDF Study", "🎵 Audio Study", "🎬 Video Study"])

with tab1:
    st.markdown('<div class="study-card">', unsafe_allow_html=True)
    st.markdown("## 📄 PDF Study Module")
    
    st.markdown("### Upload PDF files")
    uploaded_pdf = st.file_uploader(
        "Drag and drop files here",
        type=['pdf'],
        help="Limit 200MB per file • PDF",
        key="pdf_uploader"
    )
    
    if uploaded_pdf:
        st.success(f"✅ PDF '{uploaded_pdf.name}' uploaded successfully!")
        
        if uploaded_pdf.name not in st.session_state.processed_sources:
            st.session_state.processed_sources.append(uploaded_pdf.name)
        
        # File info display
        file_size = len(uploaded_pdf.getvalue()) / (1024 * 1024)  # Convert to MB
        st.info(f"📄 {uploaded_pdf.name} - {file_size:.1f}MB")
    
    st.markdown("### 💬 Ask Questions")
    st.markdown("Ask a question about your PDF:")
    
    question = st.text_input("", placeholder="What is the main topic discussed in the document?", key="pdf_question")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        ask_button = st.button("🔍 Ask Question", key="pdf_ask", use_container_width=True)
    with col2:
        if st.session_state.qa_history:
            if st.button("📥 Download Q&A", key="download_qa", use_container_width=True):
                pdf_buffer = create_qa_pdf(st.session_state.qa_history)
                st.download_button(
                    label="📄 Download PDF Report",
                    data=pdf_buffer,
                    file_name=f"StudyMate_QA_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf",
                    key="download_pdf_report"
                )
    
    if ask_button:
        if question and uploaded_pdf:
            with st.spinner("🤖 Processing your question... This may take a moment."):
                result = call_flask_api(source=uploaded_pdf, question=question)
                
                if "error" in result:
                    st.error(f"❌ Error: {result['error']}")
                else:
                    # Display Q&A
                    st.markdown('<div class="question-box">', unsafe_allow_html=True)
                    st.markdown(f"**❓ Question:** {question}")
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    st.markdown('<div class="answer-box">', unsafe_allow_html=True)
                    st.markdown(f"**🤖 Answer:** {result.get('answer', 'No answer provided')}")
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Save to history
                    qa_entry = {
                        "timestamp": datetime.now().isoformat(),
                        "source": result.get('source_name', uploaded_pdf.name),
                        "source_type": result.get('source_type', 'file'),
                        "question": question,
                        "answer": result.get('answer', 'No answer provided')
                    }
                    st.session_state.qa_history.append(qa_entry)
                    
                    st.success(f"✅ {result.get('message', 'Answer generated successfully!')}")
                    
        elif not uploaded_pdf:
            st.warning("⚠️ Please upload a PDF file first.")
        elif not question:
            st.warning("⚠️ Please enter a question.")
    
    st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="study-card">', unsafe_allow_html=True)
    st.markdown("## 🎵 Audio Study Module")
    
    st.markdown("### Upload Audio files")
    uploaded_audio = st.file_uploader(
        "Drag and drop audio files here",
        type=['mp3', 'wav'],
        help="Limit 200MB per file • MP3, WAV",
        key="audio_uploader"
    )
    
    if uploaded_audio:
        st.success(f"✅ Audio '{uploaded_audio.name}' uploaded successfully!")
        st.audio(uploaded_audio, format='audio/mp3')
        
        if uploaded_audio.name not in st.session_state.processed_sources:
            st.session_state.processed_sources.append(uploaded_audio.name)
    
    st.markdown("### 💬 Ask Questions")
    question_audio = st.text_input("Ask about your audio content:", placeholder="What are the key points discussed in the audio?", key="audio_question")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        ask_audio_button = st.button("🔍 Ask Question", key="audio_ask", use_container_width=True)
    with col2:
        if st.session_state.qa_history:
            if st.button("📥 Download Q&A", key="download_audio_qa", use_container_width=True):
                pdf_buffer = create_qa_pdf(st.session_state.qa_history)
                st.download_button(
                    label="📄 Download PDF Report",
                    data=pdf_buffer,
                    file_name=f"StudyMate_Audio_QA_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf",
                    key="download_audio_pdf_report"
                )
    
    if ask_audio_button:
        if question_audio and uploaded_audio:
            with st.spinner("🎵 Transcribing and processing audio... This may take a while."):
                result = call_flask_api(source=uploaded_audio, question=question_audio)
                
                if "error" in result:
                    st.error(f"❌ Error: {result['error']}")
                else:
                    # Display Q&A
                    st.markdown('<div class="question-box">', unsafe_allow_html=True)
                    st.markdown(f"**❓ Question:** {question_audio}")
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    st.markdown('<div class="answer-box">', unsafe_allow_html=True)
                    st.markdown(f"**🤖 Answer:** {result.get('answer', 'No answer provided')}")
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Save to history
                    qa_entry = {
                        "timestamp": datetime.now().isoformat(),
                        "source": result.get('source_name', uploaded_audio.name),
                        "source_type": result.get('source_type', 'file'),
                        "question": question_audio,
                        "answer": result.get('answer', 'No answer provided')
                    }
                    st.session_state.qa_history.append(qa_entry)
                    
                    st.success(f"✅ {result.get('message', 'Answer generated successfully!')}")
        elif not uploaded_audio:
            st.warning("⚠️ Please upload an audio file first.")
        elif not question_audio:
            st.warning("⚠️ Please enter a question.")
    
    st.markdown('</div>', unsafe_allow_html=True)

with tab3:
    st.markdown('<div class="study-card">', unsafe_allow_html=True)
    st.markdown("## 🎬 Video Study Module")
    
    st.markdown("### Enter YouTube Video URL")
    youtube_url = st.text_input(
        "Paste YouTube URL here",
        placeholder="e.g., https://www.youtube.com/watch?v=VIDEO_ID",
        key="youtube_url"
    )
    
    if youtube_url:
        st.success(f"✅ YouTube URL '{youtube_url}' entered successfully!")
        if youtube_url not in st.session_state.processed_sources:
            st.session_state.processed_sources.append(youtube_url)
        st.video(youtube_url)
    
    st.markdown("### 💬 Ask Questions")
    question_video = st.text_input(
        "Ask about your video content:",
        placeholder="What are the key points discussed in the video?",
        key="video_question"
    )
    
    col1, col2 = st.columns([3, 1])
    with col1:
        ask_video_button = st.button("🔍 Ask Question", key="video_ask", use_container_width=True)
    with col2:
        if st.session_state.qa_history:
            if st.button("📥 Download Q&A", key="download_video_qa", use_container_width=True):
                pdf_buffer = create_qa_pdf(st.session_state.qa_history)
                st.download_button(
                    label="📄 Download PDF Report",
                    data=pdf_buffer,
                    file_name=f"StudyMate_Video_QA_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf",
                    key="download_video_pdf_report"
                )
    
    if ask_video_button:
        if question_video and youtube_url:
            with st.spinner("🎥 Processing video transcript... This may take a moment."):
                result = call_flask_api(youtube_url=youtube_url, question=question_video)
                
                if "error" in result:
                    st.error(f"❌ Error: {result['error']}")
                else:
                    # Display Q&A
                    st.markdown('<div class="question-box">', unsafe_allow_html=True)
                    st.markdown(f"**❓ Question:** {question_video}")
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    st.markdown('<div class="answer-box">', unsafe_allow_html=True)
                    st.markdown(f"**🤖 Answer:** {result.get('answer', 'No answer provided')}")
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Save to history
                    qa_entry = {
                        "timestamp": datetime.now().isoformat(),
                        "source": result.get('source_name', youtube_url),
                        "source_type": result.get('source_type', 'youtube'),
                        "question": question_video,
                        "answer": result.get('answer', 'No answer provided')
                    }
                    st.session_state.qa_history.append(qa_entry)
                    
                    st.success(f"✅ {result.get('message', 'Answer generated successfully!')}")
        elif not youtube_url:
            st.warning("⚠️ Please enter a YouTube URL first.")
        elif not question_video:
            st.warning("⚠️ Please enter a question.")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Q&A History Section
if st.session_state.qa_history:
    st.markdown("---")
    st.markdown("## 📚 Q&A History")
    
    with st.expander(f"View {len(st.session_state.qa_history)} Previous Questions", expanded=False):
        for i, qa in enumerate(reversed(st.session_state.qa_history[-5:]), 1):  # Show last 5
            st.markdown('<div class="study-card">', unsafe_allow_html=True)
            st.markdown(f"**Source ({qa['source_type'].capitalize()}):** {qa['source']}")
            st.markdown(f"**❓ Q{len(st.session_state.qa_history)-i+1}:** {qa['question']}")
            st.markdown(f"**🤖 Answer:** {qa['answer'][:200]}{'...' if len(qa['answer']) > 200 else ''}")
            st.markdown(f"**📅 Time:** {datetime.fromisoformat(qa['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}")
            st.markdown('</div>', unsafe_allow_html=True)

# Footer with additional features
st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown('<div class="study-card">', unsafe_allow_html=True)
    st.markdown("### 📊 Study Statistics")
    st.metric("Sources Processed", len(st.session_state.processed_sources))
    st.metric("Questions Asked", len(st.session_state.qa_history))
    st.metric("Active Sessions", 1)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="study-card">', unsafe_allow_html=True)
    st.markdown("### ⚡ Quick Actions")
    if st.button("🔄 Clear History", key="clear_history"):
        st.session_state.qa_history = []
        st.session_state.processed_sources = []
        st.success("History cleared!")
        st.rerun()
    if st.button("📊 Export All Data", key="export_data"):
        if st.session_state.qa_history:
            pdf_buffer = create_qa_pdf(st.session_state.qa_history)
            st.download_button(
                label="📥 Download Complete Report",
                data=pdf_buffer,
                file_name=f"StudyMate_Complete_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                mime="application/pdf",
                key="download_complete_report"
            )
        else:
            st.info("No Q&A history to export!")
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="study-card">', unsafe_allow_html=True)
    st.markdown("### 🎯 Study Goals")
    progress = min(100, len(st.session_state.qa_history) * 10)
    st.progress(progress / 100)
    st.markdown(f"Progress: {progress}%")
    st.markdown("*Ask more questions to increase progress!*")
    st.markdown('</div>', unsafe_allow_html=True)