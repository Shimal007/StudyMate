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
import json
# Page configuration
st.set_page_config(
    page_title="StudyMate - AI Learning Platform",
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
   
    /* Quiz question styling */
    .quiz-question {
        background: rgba(99, 102, 241, 0.1);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        color: #ffffff;
    }
   
    /* Quiz result styling */
    .quiz-result-correct {
        background: rgba(16, 185, 129, 0.1);
        border: 1px solid rgba(16, 185, 129, 0.3);
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        color: #10b981;
    }
   
    .quiz-result-incorrect {
        background: rgba(239, 68, 68, 0.1);
        border: 1px solid rgba(239, 68, 68, 0.3);
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        color: #ef4444;
    }
   
    /* Score card styling */
    .score-card {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.2), rgba(168, 85, 247, 0.2));
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 20px;
        padding: 2rem;
        text-align: center;
        margin: 2rem 0;
        backdrop-filter: blur(10px);
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
   
    /* Study card styling */
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
        cursor: pointer;
    }
   
    .sidebar-menu:hover {
        background: rgba(99, 102, 241, 0.1);
        transform: translateX(5px);
    }
   
    /* Progress bar styling */
    .stProgress > div > div > div > div {
        background: linear-gradient(135deg, #6366f1, #a855f7);
    }
   
    /* File uploader styling */
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
   
    /* Navigation button styling */
    .nav-button {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(168, 85, 247, 0.1));
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 15px;
        padding: 1rem;
        margin: 0.5rem 0;
        cursor: pointer;
        transition: all 0.3s ease;
        text-align: left;
    }
   
    .nav-button:hover {
        background: rgba(99, 102, 241, 0.2);
        transform: translateX(5px);
    }
   
    .nav-button-active {
        background: linear-gradient(135deg, #6366f1, #a855f7);
        border-color: rgba(99, 102, 241, 0.6);
    }
</style>
""", unsafe_allow_html=True)
# Configuration
FLASK_API_URL = "http://localhost:5000/api/answer-question"
FLASK_QUIZ_API_URL = "http://localhost:5000/api/generate-quiz"
FLASK_EVAL_API_URL = "http://localhost:5000/api/evaluate-quiz"
FLASK_PLAN_API_URL = "http://localhost:5000/api/generate-study-plan"
# Initialize session state
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'study'
if 'processed_sources' not in st.session_state:
    st.session_state.processed_sources = []
if 'qa_history' not in st.session_state:
    st.session_state.qa_history = []
if 'quiz_data' not in st.session_state:
    st.session_state.quiz_data = None
if 'quiz_id' not in st.session_state:
    st.session_state.quiz_id = None
if 'user_answers' not in st.session_state:
    st.session_state.user_answers = []
if 'quiz_submitted' not in st.session_state:
    st.session_state.quiz_submitted = False
if 'quiz_results' not in st.session_state:
    st.session_state.quiz_results = None
if 'quiz_history' not in st.session_state:
    st.session_state.quiz_history = []
if 'study_plan' not in st.session_state:
    st.session_state.study_plan = None
if 'plans_generated' not in st.session_state:
    st.session_state.plans_generated = 0
# Function to call Flask API for Q&A
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
            return {"error": error_data.get('error', 'Unknown error'), "request_id": error_data.get('request_id', 'N/A')}
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to Flask server. Please ensure it's running on http://localhost:5000", "request_id": "N/A"}
    except requests.exceptions.Timeout:
        return {"error": "Request timed out. The file or video might be too large or processing is taking too long.", "request_id": "N/A"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}", "request_id": "N/A"}
# Function to call Flask API for quiz generation
def generate_quiz_api(source=None, youtube_url=None, num_questions=5, difficulty='medium'):
    """Call the Flask API to generate quiz"""
    try:
        data = {
            'num_questions': num_questions,
            'difficulty': difficulty
        }
        files = None
        
        if youtube_url:
            data['youtube_url'] = youtube_url
        elif source:
            files = {'file': (source.name, source.getvalue(), source.type)}
        
        response = requests.post(FLASK_QUIZ_API_URL, files=files, data=data, timeout=120)
        
        if response.status_code == 200:
            return response.json()
        else:
            error_data = response.json() if response.headers.get('content-type') == 'application/json' else {"error": response.text}
            return {"error": error_data.get('error', 'Unknown error'), "request_id": error_data.get('request_id', 'N/A')}
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to Flask server. Please ensure it's running on http://localhost:5000", "request_id": "N/A"}
    except requests.exceptions.Timeout:
        return {"error": "Request timed out. The file or video might be too large or processing is taking too long.", "request_id": "N/A"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}", "request_id": "N/A"}
# Function to call Flask API for study plan generation
def generate_study_plan_api(source=None, num_days=7):
    """Call the Flask API to generate study plan"""
    try:
        data = {'num_days': num_days}
        files = None
        
        if source:
            files = {'file': (source.name, source.getvalue(), source.type)}
        
        response = requests.post(FLASK_PLAN_API_URL, files=files, data=data, timeout=120)
        
        if response.status_code == 200:
            return response.json()
        else:
            error_data = response.json() if response.headers.get('content-type') == 'application/json' else {"error": response.text}
            return {"error": error_data.get('error', 'Unknown error'), "request_id": error_data.get('request_id', 'N/A')}
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to Flask server. Please ensure it's running on http://localhost:5000", "request_id": "N/A"}
    except requests.exceptions.Timeout:
        return {"error": "Request timed out. The file or video might be too large or processing is taking too long.", "request_id": "N/A"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}", "request_id": "N/A"}
# Function to evaluate quiz
def evaluate_quiz_api(quiz_id, user_answers):
    """Call the Flask API to evaluate quiz"""
    try:
        data = {
            'quiz_id': quiz_id,
            'user_answers': user_answers
        }
        
        response = requests.post(
            FLASK_EVAL_API_URL,
            json=data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            error_data = response.json() if response.headers.get('content-type') == 'application/json' else {"error": response.text}
            return {"error": error_data.get('error', 'Unknown error')}
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to Flask server. Please ensure it's running on http://localhost:5000"}
    except requests.exceptions.Timeout:
        return {"error": "Request timed out while evaluating quiz."}
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
# Function to create PDF from quiz results
def create_quiz_pdf(quiz_data, user_answers, results):
    """Create a PDF document from quiz results"""
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
        spaceAfter=10,
        leftIndent=20
    )
   
    # Build content
    content = []
   
    # Title
    content.append(Paragraph("StudyMate - Quiz Results Report", title_style))
    content.append(Spacer(1, 20))
   
    # Score summary
    content.append(Paragraph(f"Final Score: {results['score']:.1f}%", styles['Heading2']))
    content.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    content.append(Paragraph(f"Total Questions: {len(quiz_data['questions'])}", styles['Normal']))
    content.append(Spacer(1, 30))
   
    # Questions and answers
    for i, question_data in enumerate(quiz_data['questions']):
        result_detail = results['details'][i]
        
        # Question
        content.append(Paragraph(f"Q{i+1}: {question_data['question']}", question_style))
        
        # Options
        for j, option in enumerate(question_data['options']):
            marker = "✓" if j == user_answers[i] else "  "
            content.append(Paragraph(f"{marker} {option}", answer_style))
        
        # Result
        if result_detail['is_correct']:
            content.append(Paragraph(f"✅ Correct! Your answer: {result_detail['user_answer']}", answer_style))
        else:
            content.append(Paragraph(f"❌ Incorrect. Your answer: {result_detail['user_answer']}, Correct: {result_detail['correct_answer']}", answer_style))
        
        # Explanation
        content.append(Paragraph(f"Explanation: {result_detail['explanation']}", answer_style))
        content.append(Spacer(1, 15))
   
    # Build PDF
    doc.build(content)
    buffer.seek(0)
    return buffer
# Sidebar Navigation
with st.sidebar:
    st.markdown("<h1 style='color: #6366f1; text-align: center;'>🎓 StudyMate</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #a1a1aa;'>AI-Powered Learning Platform</p>", unsafe_allow_html=True)
   
    # API Status Check
    try:
        status_response = requests.get("http://localhost:5000", timeout=5)
        st.success("✅ Flask Server Connected")
    except:
        st.error("❌ Flask Server Disconnected")
        st.info("Please start the Flask server:\n```bash\npython app.py\n```")
   
    st.markdown("---")
   
    # Navigation Menu
    st.markdown("### 🧭 Navigation")
   
    nav_options = [
        ("📚 Study Center", "study"),
        ("📅 Study Planner", "planner"),
        ("📝 Quiz Center", "quiz"),
        ("📊 Analytics", "analytics"),
        ("⚙️ Settings", "settings")
    ]
   
    for option_name, option_key in nav_options:
        button_class = "nav-button-active" if st.session_state.current_page == option_key else "nav-button"
        if st.button(option_name, key=f"nav_{option_key}", use_container_width=True):
            st.session_state.current_page = option_key
            st.rerun()
   
    st.markdown("---")
   
    # Quick Stats based on current page
    if st.session_state.current_page == 'study':
        st.markdown("### 📈 Study Stats")
        st.metric("Sources Processed", len(st.session_state.processed_sources))
        st.metric("Questions Asked", len(st.session_state.qa_history))
    elif st.session_state.current_page == 'planner':
        st.markdown("### 📅 Plan Stats")
        st.metric("Plans Generated", st.session_state.plans_generated)
    elif st.session_state.current_page == 'quiz':
        st.markdown("### 🎯 Quiz Stats")
        st.metric("Quizzes Taken", len(st.session_state.quiz_history))
        if st.session_state.quiz_history:
            avg_score = sum([quiz['score'] for quiz in st.session_state.quiz_history]) / len(st.session_state.quiz_history)
            st.metric("Average Score", f"{avg_score:.1f}%")
   
    st.markdown("---")
   
    # Quick Actions
    st.markdown("### ⚡ Quick Actions")
    if st.button("🔄 Reset All Data", key="reset_all"):
        st.session_state.processed_sources = []
        st.session_state.qa_history = []
        st.session_state.quiz_history = []
        st.session_state.quiz_data = None
        st.session_state.quiz_id = None
        st.session_state.user_answers = []
        st.session_state.quiz_submitted = False
        st.session_state.quiz_results = None
        st.session_state.study_plan = None
        st.session_state.plans_generated = 0
        st.success("All data reset!")
        st.rerun()
# Main Content Area
if st.session_state.current_page == 'study':
    st.markdown('<h1 class="main-title">📚 Study Center</h1>', unsafe_allow_html=True)
   
    # Study Mode Tabs
    tab1, tab2, tab3 = st.tabs(["📄 PDF Study", "🎵 Audio Study", "🎬 Video Study"])
   
    with tab1:
        st.markdown('<div class="study-card">', unsafe_allow_html=True)
        st.markdown("## 📄 PDF Study Module")
        
        uploaded_pdf = st.file_uploader(
            "Upload PDF files for studying",
            type=['pdf'],
            help="Upload a PDF file to ask questions about its content",
            key="study_pdf_uploader"
        )
        
        if uploaded_pdf:
            st.success(f"✅ PDF '{uploaded_pdf.name}' uploaded successfully!")
            
            if uploaded_pdf.name not in st.session_state.processed_sources:
                st.session_state.processed_sources.append(uploaded_pdf.name)
            
            # File info display
            file_size = len(uploaded_pdf.getvalue()) / (1024 * 1024)  # Convert to MB
            st.info(f"📄 {uploaded_pdf.name} - {file_size:.1f}MB")
        
        st.markdown("### 💬 Ask Questions")
        question = st.text_input("Ask a question about your PDF:", placeholder="What is the main topic discussed in the document?", key="pdf_question")
        
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
                        st.error(f"❌ Error: {result['error']} (Request ID: {result['request_id']})")
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
        
        uploaded_audio = st.file_uploader(
            "Upload Audio files for studying",
            type=['mp3', 'wav'],
            help="Upload an audio file to ask questions about its content",
            key="study_audio_uploader"
        )
        
        if uploaded_audio:
            st.success(f"✅ Audio '{uploaded_audio.name}' uploaded successfully!")
            st.audio(uploaded_audio, format='audio/mp3')
            
            if uploaded_audio.name not in st.session_state.processed_sources:
                st.session_state.processed_sources.append(uploaded_audio.name)
        
        question_audio = st.text_input("Ask about your audio content:", placeholder="What are the key points discussed in the audio?", key="audio_question")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            ask_audio_button = st.button("🔍 Ask Question", key="audio_ask", use_container_width=True)
        with col2:
            if st.session_state.qa_history:
                if st.button("📥 Download Q&A", key="download_qa_audio", use_container_width=True):
                    pdf_buffer = create_qa_pdf(st.session_state.qa_history)
                    st.download_button(
                        label="📄 Download PDF Report",
                        data=pdf_buffer,
                        file_name=f"StudyMate_QA_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        mime="application/pdf",
                        key="download_pdf_report_audio"
                    )
        
        if ask_audio_button:
            if question_audio and uploaded_audio:
                with st.spinner("🎵 Transcribing and processing audio... This may take a while."):
                    result = call_flask_api(source=uploaded_audio, question=question_audio)
                    
                    if "error" in result:
                        st.error(f"❌ Error: {result['error']} (Request ID: {result['request_id']})")
                    else:
                        st.markdown('<div class="question-box">', unsafe_allow_html=True)
                        st.markdown(f"**❓ Question:** {question_audio}")
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        st.markdown('<div class="answer-box">', unsafe_allow_html=True)
                        st.markdown(f"**🤖 Answer:** {result.get('answer', 'No answer provided')}")
                        st.markdown('</div>', unsafe_allow_html=True)
                        
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
        
        youtube_url = st.text_input(
            "Enter YouTube Video URL for studying",
            placeholder="e.g., https://www.youtube.com/watch?v=VIDEO_ID",
            key="study_youtube_url"
        )
        
        if youtube_url:
            st.success(f"✅ YouTube URL entered successfully!")
            if youtube_url not in st.session_state.processed_sources:
                st.session_state.processed_sources.append(youtube_url)
            st.video(youtube_url)
        
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
                if st.button("📥 Download Q&A", key="download_qa_video", use_container_width=True):
                    pdf_buffer = create_qa_pdf(st.session_state.qa_history)
                    st.download_button(
                        label="📄 Download PDF Report",
                        data=pdf_buffer,
                        file_name=f"StudyMate_QA_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        mime="application/pdf",
                        key="download_pdf_report_video"
                    )
        
        if ask_video_button:
            if question_video and youtube_url:
                with st.spinner("🎥 Processing video transcript... This may take a moment."):
                    result = call_flask_api(youtube_url=youtube_url, question=question_video)
                    
                    if "error" in result:
                        st.error(f"❌ Error: {result['error']} (Request ID: {result['request_id']})")
                    else:
                        st.markdown('<div class="question-box">', unsafe_allow_html=True)
                        st.markdown(f"**❓ Question:** {question_video}")
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        st.markdown('<div class="answer-box">', unsafe_allow_html=True)
                        st.markdown(f"**🤖 Answer:** {result.get('answer', 'No answer provided')}")
                        st.markdown('</div>', unsafe_allow_html=True)
                        
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
            for i, qa in enumerate(reversed(st.session_state.qa_history[-5:]), 1):
                st.markdown('<div class="study-card">', unsafe_allow_html=True)
                st.markdown(f"**Source ({qa['source_type'].capitalize()}):** {qa['source']}")
                st.markdown(f"**❓ Q{len(st.session_state.qa_history)-i+1}:** {qa['question']}")
                st.markdown(f"**🤖 Answer:** {qa['answer'][:200]}{'...' if len(qa['answer']) > 200 else ''}")
                st.markdown(f"**📅 Time:** {datetime.fromisoformat(qa['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}")
                st.markdown('</div>', unsafe_allow_html=True)
elif st.session_state.current_page == 'planner':
    st.markdown('<h1 class="main-title">📅 Study Planner</h1>', unsafe_allow_html=True)
    
    tab1, = st.tabs(["📄 PDF Study Plan"])
    
    with tab1:
        st.markdown('<div class="study-card">', unsafe_allow_html=True)
        st.markdown("## 📄 Generate Study Plan from PDF")
        
        uploaded_pdf = st.file_uploader(
            "Upload PDF file for study plan",
            type=['pdf'],
            help="Upload a PDF file to generate a study plan",
            key="plan_pdf_uploader"
        )
        
        if uploaded_pdf:
            st.success(f"✅ PDF '{uploaded_pdf.name}' uploaded successfully!")
            
            num_days = st.selectbox(
                "Select number of days to complete the study",
                options=[3, 5, 7, 10, 14, 21, 30],
                index=2,
                key="plan_num_days"
            )
            
            col1, col2 = st.columns([3, 1])
            with col1:
                generate_plan_button = st.button(f"📅 Generate Study Plan for {num_days} Days", key="generate_plan", use_container_width=True)
            with col2:
                st.write(f"Days: {num_days}")
            
            if generate_plan_button:
                if uploaded_pdf:
                    with st.spinner("🗓️ Generating study plan... This may take a moment."):
                        result = generate_study_plan_api(source=uploaded_pdf, num_days=num_days)
                        
                        if "error" in result:
                            st.error(f"❌ Error: {result['error']} (Request ID: {result.get('request_id', 'N/A')})")
                        else:
                            st.session_state.study_plan = result
                            st.session_state.plans_generated += 1
                            st.success(f"✅ Study plan generated successfully for {num_days} days!")
                            st.rerun()
                else:
                    st.warning("⚠️ Please upload a PDF file first.")
        
        if st.session_state.study_plan:
            st.markdown("---")
            st.markdown("## 📋 Your Study Plan")
            
            for day_data in st.session_state.study_plan.get('days', []):
                with st.expander(f"**Day {day_data['day']}**: {', '.join(day_data['topics'][:3])}{'...' if len(day_data['topics']) > 3 else ''}"):
                    st.markdown("### **Topics to Cover:**")
                    for topic in day_data['topics']:
                        st.markdown(f"- {topic}")
                    
                    st.markdown("### **Suggested Tasks:**")
                    for task in day_data['tasks']:
                        st.markdown(f"- {task}")
                    
                    estimated_time = day_data.get('estimated_time', '2-3 hours')
                    st.markdown(f"### **Estimated Time:** {estimated_time}")
        
        st.markdown('</div>', unsafe_allow_html=True)
elif st.session_state.current_page == 'quiz':
    st.markdown('<h1 class="main-title">📝 Quiz Center</h1>', unsafe_allow_html=True)
   
    # Quiz Configuration in sidebar for quiz page
    if 'num_questions' not in st.session_state:
        st.session_state.num_questions = 5
    if 'difficulty' not in st.session_state:
        st.session_state.difficulty = 'medium'
   
    with st.sidebar:
        st.markdown("### 🎯 Quiz Settings")
        
        num_questions = st.selectbox(
            "Number of Questions",
            options=[3, 5, 8, 10, 15, 20],
            index=1,
            key="quiz_num_questions"
        )
        
        difficulty = st.selectbox(
            "Difficulty Level",
            options=['easy', 'medium', 'hard'],
            index=1,
            key="quiz_difficulty"
        )
        
        if st.button("🔄 Reset Quiz", key="reset_quiz"):
            st.session_state.quiz_data = None
            st.session_state.quiz_id = None
            st.session_state.user_answers = []
            st.session_state.quiz_submitted = False
            st.session_state.quiz_results = None
            st.success("Quiz reset!")
            st.rerun()
   
    # Quiz Generation Tabs
    tab1, tab2, tab3 = st.tabs(["📄 PDF Quiz", "🎵 Audio Quiz", "🎬 Video Quiz"])
   
    with tab1:
        st.markdown('<div class="study-card">', unsafe_allow_html=True)
        st.markdown("## 📄 Generate Quiz from PDF")
        
        uploaded_pdf = st.file_uploader(
            "Upload PDF file for quiz generation",
            type=['pdf'],
            help="Upload a PDF file to generate quiz questions",
            key="quiz_pdf_uploader"
        )
        
        if uploaded_pdf:
            st.success(f"✅ PDF '{uploaded_pdf.name}' uploaded successfully!")
            
            col1, col2 = st.columns([3, 1])
            with col1:
                generate_button = st.button(f"🎯 Generate {num_questions} {difficulty.title()} Questions", key="generate_pdf_quiz", use_container_width=True)
            with col2:
                st.write(f"Questions: {num_questions}")
                st.write(f"Level: {difficulty.title()}")
            
            if generate_button:
                if not st.session_state.quiz_submitted:
                    with st.spinner("🎯 Generating quiz questions... This may take a moment."):
                        result = generate_quiz_api(source=uploaded_pdf, num_questions=num_questions, difficulty=difficulty)
                        
                        if "error" in result:
                            st.error(f"❌ Error: {result['error']} (Request ID: {result['request_id']})")
                        else:
                            st.session_state.quiz_data = result
                            st.session_state.quiz_id = result['quiz_id']
                            st.session_state.user_answers = [-1] * len(result['questions'])
                            st.session_state.quiz_submitted = False
                            st.session_state.quiz_results = None
                            st.success(f"✅ Quiz generated successfully with {len(result['questions'])} questions!")
                            st.rerun()
                else:
                    st.warning("⚠️ Please reset the current quiz before generating a new one.")
        
        st.markdown('</div>', unsafe_allow_html=True)
   
    with tab2:
        st.markdown('<div class="study-card">', unsafe_allow_html=True)
        st.markdown("## 🎵 Generate Quiz from Audio")
        
        uploaded_audio = st.file_uploader(
            "Upload Audio file for quiz generation",
            type=['mp3', 'wav'],
            help="Upload an audio file to generate quiz questions",
            key="quiz_audio_uploader"
        )
        
        if uploaded_audio:
            st.success(f"✅ Audio '{uploaded_audio.name}' uploaded successfully!")
            st.audio(uploaded_audio, format='audio/mp3')
            
            col1, col2 = st.columns([3, 1])
            with col1:
                generate_audio_button = st.button(f"🎯 Generate {num_questions} {difficulty.title()} Questions", key="generate_audio_quiz", use_container_width=True)
            with col2:
                st.write(f"Questions: {num_questions}")
                st.write(f"Level: {difficulty.title()}")
            
            if generate_audio_button:
                if not st.session_state.quiz_submitted:
                    with st.spinner("🎵 Transcribing audio and generating quiz... This may take a while."):
                        result = generate_quiz_api(source=uploaded_audio, num_questions=num_questions, difficulty=difficulty)
                        
                        if "error" in result:
                            st.error(f"❌ Error: {result['error']} (Request ID: {result['request_id']})")
                        else:
                            st.session_state.quiz_data = result
                            st.session_state.quiz_id = result['quiz_id']
                            st.session_state.user_answers = [-1] * len(result['questions'])
                            st.session_state.quiz_submitted = False
                            st.session_state.quiz_results = None
                            st.success(f"✅ Quiz generated successfully with {len(result['questions'])} questions!")
                            st.rerun()
                else:
                    st.warning("⚠️ Please reset the current quiz before generating a new one.")
        
        st.markdown('</div>', unsafe_allow_html=True)
   
    with tab3:
        st.markdown('<div class="study-card">', unsafe_allow_html=True)
        st.markdown("## 🎬 Generate Quiz from YouTube Video")
        
        youtube_url = st.text_input(
            "Enter YouTube URL for quiz generation",
            placeholder="e.g., https://www.youtube.com/watch?v=VIDEO_ID",
            key="quiz_youtube_url"
        )
        
        if youtube_url:
            st.success(f"✅ YouTube URL entered successfully!")
            st.video(youtube_url)
            
            col1, col2 = st.columns([3, 1])
            with col1:
                generate_video_button = st.button(f"🎯 Generate {num_questions} {difficulty.title()} Questions", key="generate_video_quiz", use_container_width=True)
            with col2:
                st.write(f"Questions: {num_questions}")
                st.write(f"Level: {difficulty.title()}")
            
            if generate_video_button:
                if not st.session_state.quiz_submitted:
                    with st.spinner("🎥 Processing video transcript and generating quiz... This may take a moment."):
                        result = generate_quiz_api(youtube_url=youtube_url, num_questions=num_questions, difficulty=difficulty)
                        
                        if "error" in result:
                            st.error(f"❌ Error: {result['error']} (Request ID: {result['request_id']})")
                        else:
                            st.session_state.quiz_data = result
                            st.session_state.quiz_id = result['quiz_id']
                            st.session_state.user_answers = [-1] * len(result['questions'])
                            st.session_state.quiz_submitted = False
                            st.session_state.quiz_results = None
                            st.success(f"✅ Quiz generated successfully with {len(result['questions'])} questions!")
                            st.rerun()
                else:
                    st.warning("⚠️ Please reset the current quiz before generating a new one.")
        
        st.markdown('</div>', unsafe_allow_html=True)
   
    # Quiz Display and Taking Section
    if st.session_state.quiz_data and not st.session_state.quiz_submitted:
        st.markdown("---")
        st.markdown("## 📝 Take Quiz")
        
        # Progress bar
        answered_questions = sum(1 for answer in st.session_state.user_answers if answer != -1)
        total_questions = len(st.session_state.quiz_data['questions'])
        progress = answered_questions / total_questions
        
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.progress(progress)
        with col2:
            st.metric("Progress", f"{answered_questions}/{total_questions}")
        with col3:
            st.metric("Completion", f"{progress*100:.0f}%")
        
        # Display questions
        for i, question_data in enumerate(st.session_state.quiz_data['questions']):
            st.markdown('<div class="quiz-question">', unsafe_allow_html=True)
            st.markdown(f"### Question {i+1}")
            st.markdown(f"**{question_data['question']}**")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Display options as radio buttons
            selected_option = st.radio(
                f"Select your answer for question {i+1}:",
                options=range(len(question_data['options'])),
                format_func=lambda x: question_data['options'][x],
                key=f"question_{i}",
                index=st.session_state.user_answers[i] if st.session_state.user_answers[i] != -1 else None
            )
            
            # Update user answers
            st.session_state.user_answers[i] = selected_option
            
            st.markdown("---")
        
        # Submit quiz button
        if answered_questions == total_questions:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("📋 Submit Quiz", key="submit_quiz", use_container_width=True):
                    with st.spinner("📊 Evaluating your quiz..."):
                        eval_result = evaluate_quiz_api(st.session_state.quiz_id, st.session_state.user_answers)
                        
                        if "error" in eval_result:
                            st.error(f"❌ Error evaluating quiz: {eval_result['error']}")
                        else:
                            st.session_state.quiz_results = eval_result
                            st.session_state.quiz_submitted = True
                            
                            # Add to history
                            quiz_history_entry = {
                                "timestamp": datetime.now().isoformat(),
                                "score": eval_result['score'],
                                "total_questions": total_questions,
                                "difficulty": difficulty,
                                "source_type": st.session_state.quiz_data.get('source_type', 'Unknown')
                            }
                            st.session_state.quiz_history.append(quiz_history_entry)
                            
                            st.success("✅ Quiz submitted successfully!")
                            st.rerun()
        else:
            st.info(f"📝 Please answer all questions to submit the quiz. ({answered_questions}/{total_questions} completed)")
   
    # Quiz Results Section
    if st.session_state.quiz_results and st.session_state.quiz_submitted:
        st.markdown("---")
        st.markdown("## 📊 Quiz Results")
        
        # Score display
        score = st.session_state.quiz_results['score']
        st.markdown('<div class="score-card">', unsafe_allow_html=True)
        st.markdown(f"# 🎯 Your Score: {score:.1f}%")
        
        if score >= 90:
            st.markdown("## 🏆 Excellent! Outstanding performance!")
        elif score >= 80:
            st.markdown("## 🎉 Great job! Very good performance!")
        elif score >= 70:
            st.markdown("## 👍 Good work! Keep it up!")
        elif score >= 60:
            st.markdown("## 📚 Not bad! Room for improvement!")
        else:
            st.markdown("## 💪 Keep studying! You'll do better next time!")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Detailed results
        st.markdown("### 📋 Detailed Results")
        
        for i, (question_data, result_detail) in enumerate(zip(st.session_state.quiz_data['questions'], st.session_state.quiz_results['details'])):
            result_class = "quiz-result-correct" if result_detail['is_correct'] else "quiz-result-incorrect"
            icon = "✅" if result_detail['is_correct'] else "❌"
            
            st.markdown(f'<div class="{result_class}">', unsafe_allow_html=True)
            st.markdown(f"### {icon} Question {i+1}")
            st.markdown(f"**{question_data['question']}**")
            st.markdown(f"**Your Answer:** {result_detail['user_answer']}")
            st.markdown(f"**Correct Answer:** {result_detail['correct_answer']}")
            st.markdown(f"**Explanation:** {result_detail['explanation']}")
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown("---")
        
        # Actions
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📥 Download Results", key="download_results"):
                pdf_buffer = create_quiz_pdf(st.session_state.quiz_data, st.session_state.user_answers, st.session_state.quiz_results)
                st.download_button(
                    label="📄 Download PDF Report",
                    data=pdf_buffer,
                    file_name=f"StudyMate_Quiz_Results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf",
                    key="download_quiz_pdf"
                )
        
        with col2:
            if st.button("🔄 Take Another Quiz", key="retake_quiz"):
                st.session_state.quiz_data = None
                st.session_state.quiz_id = None
                st.session_state.user_answers = []
                st.session_state.quiz_submitted = False
                st.session_state.quiz_results = None
                st.rerun()
        
        with col3:
            if st.button("📚 Back to Study", key="back_to_study"):
                st.session_state.current_page = 'study'
                st.rerun()
elif st.session_state.current_page == 'analytics':
    st.markdown('<h1 class="main-title">📊 Analytics Dashboard</h1>', unsafe_allow_html=True)
   
    col1, col2 = st.columns(2)
   
    with col1:
        st.markdown('<div class="study-card">', unsafe_allow_html=True)
        st.markdown("### 📚 Study Analytics")
        st.metric("Total Sources Processed", len(st.session_state.processed_sources))
        st.metric("Questions Asked", len(st.session_state.qa_history))
        
        if st.session_state.qa_history:
            # Recent activity
            recent_qa = st.session_state.qa_history[-3:]
            st.markdown("**Recent Questions:**")
            for qa in recent_qa:
                st.markdown(f"- {qa['question'][:50]}...")
        st.markdown('</div>', unsafe_allow_html=True)
   
    with col2:
        st.markdown('<div class="study-card">', unsafe_allow_html=True)
        st.markdown("### 🎯 Quiz Analytics")
        st.metric("Quizzes Completed", len(st.session_state.quiz_history))
        
        if st.session_state.quiz_history:
            avg_score = sum([quiz['score'] for quiz in st.session_state.quiz_history]) / len(st.session_state.quiz_history)
            best_score = max([quiz['score'] for quiz in st.session_state.quiz_history])
            st.metric("Average Score", f"{avg_score:.1f}%")
            st.metric("Best Score", f"{best_score:.1f}%")
            
            # Performance by difficulty
            difficulty_stats = {'easy': [], 'medium': [], 'hard': []}
            for quiz in st.session_state.quiz_history:
                if quiz['difficulty'] in difficulty_stats:
                    difficulty_stats[quiz['difficulty']].append(quiz['score'])
            
            st.markdown("**Performance by Difficulty:**")
            for diff, scores in difficulty_stats.items():
                if scores:
                    avg = sum(scores) / len(scores)
                    st.markdown(f"- {diff.title()}: {avg:.1f}% ({len(scores)} quizzes)")
        st.markdown('</div>', unsafe_allow_html=True)
   
    # Combined History
    if st.session_state.qa_history or st.session_state.quiz_history:
        st.markdown("---")
        st.markdown("## 📈 Activity History")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.session_state.qa_history:
                st.markdown("### Recent Q&A Sessions")
                for i, qa in enumerate(reversed(st.session_state.qa_history[-5:]), 1):
                    with st.expander(f"Q{i}: {qa['question'][:50]}..."):
                        st.markdown(f"**Source:** {qa['source']}")
                        st.markdown(f"**Type:** {qa['source_type'].title()}")
                        st.markdown(f"**Answer:** {qa['answer'][:200]}...")
                        st.markdown(f"**Time:** {datetime.fromisoformat(qa['timestamp']).strftime('%Y-%m-%d %H:%M')}")
        
        with col2:
            if st.session_state.quiz_history:
                st.markdown("### Recent Quiz Results")
                for i, quiz in enumerate(reversed(st.session_state.quiz_history[-5:]), 1):
                    score_color = "🟢" if quiz['score'] >= 80 else "🟡" if quiz['score'] >= 60 else "🔴"
                    st.markdown(f"{score_color} **Quiz {i}:** {quiz['score']:.1f}% - {quiz['difficulty'].title()} ({quiz['total_questions']} questions)")
                    st.markdown(f"📅 {datetime.fromisoformat(quiz['timestamp']).strftime('%Y-%m-%d %H:%M')}")
                    st.markdown("---")
elif st.session_state.current_page == 'settings':
    st.markdown('<h1 class="main-title">⚙️ Settings & Help</h1>', unsafe_allow_html=True)
   
    col1, col2 = st.columns(2)
   
    with col1:
        st.markdown('<div class="study-card">', unsafe_allow_html=True)
        st.markdown("### 🔧 Application Settings")
        
        st.markdown("**Data Management:**")
        if st.button("🗑️ Clear All Study Data", key="clear_study_data"):
            st.session_state.qa_history = []
            st.session_state.processed_sources = []
            st.success("Study data cleared!")
            st.rerun()
        
        if st.button("🗑️ Clear All Quiz Data", key="clear_quiz_data"):
            st.session_state.quiz_history = []
            st.session_state.quiz_data = None
            st.session_state.quiz_results = None
            st.success("Quiz data cleared!")
            st.rerun()
        
        st.markdown("**Export Options:**")
        if st.session_state.qa_history:
            pdf_buffer = create_qa_pdf(st.session_state.qa_history)
            st.download_button(
                label="📥 Export All Q&A History",
                data=pdf_buffer,
                file_name=f"StudyMate_Complete_QA_History_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                mime="application/pdf",
                key="export_all_qa"
            )
        
        st.markdown('</div>', unsafe_allow_html=True)
   
    with col2:
        st.markdown('<div class="study-card">', unsafe_allow_html=True)
        st.markdown("### 📖 How to Use StudyMate")
        
        st.markdown("""
        **Study Center:**
        1. Upload PDF, audio files, or paste YouTube URLs
        2. Ask questions about the content
        3. Get AI-powered answers with explanations
        
        **Quiz Center:**
        1. Upload your study materials
        2. Configure quiz settings (difficulty, number of questions)
        3. Take the generated quiz
        4. Review detailed results with explanations
        
        **Tips for Better Results:**
        - Use clear, well-structured source materials
        - Ask specific questions for better answers
        - Review explanations to improve understanding
        - Take quizzes regularly to test knowledge
        """)
        
        st.markdown('</div>', unsafe_allow_html=True)
   
    st.markdown("---")
    st.markdown('<div class="study-card">', unsafe_allow_html=True)
    st.markdown("### 🚀 System Requirements")
   
    col1, col2, col3 = st.columns(3)
   
    with col1:
        st.markdown("**File Support:**")
        st.markdown("- PDF documents")
        st.markdown("- MP3/WAV audio")
        st.markdown("- YouTube videos")
        st.markdown("- Max file size: 200MB")
   
    with col2:
        st.markdown("**Features:**")
        st.markdown("- AI-powered Q&A")
        st.markdown("- Automated quiz generation")
        st.markdown("- Progress tracking")
        st.markdown("- PDF report exports")
   
    with col3:
        st.markdown("**Requirements:**")
        st.markdown("- Flask server running")
        st.markdown("- Internet connection")
        st.markdown("- Modern web browser")
        st.markdown("- JavaScript enabled")
   
    st.markdown('</div>', unsafe_allow_html=True)
# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #6b7280; padding: 2rem;'>"
    "🎓 StudyMate - AI-Powered Learning Platform<br>"
    "Enhance your learning with intelligent Q&A and automated assessments<br>"
    "Built with Streamlit & Flask | Powered by Ollama & SentenceTransformers"
    "</div>",
    unsafe_allow_html=True
)
