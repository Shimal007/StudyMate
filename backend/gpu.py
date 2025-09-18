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
    page_title="StudyMate - Quiz Center",
    page_icon="📝",
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
    
    /* Quiz option styling */
    .quiz-option {
        background: rgba(30, 30, 46, 0.8);
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .quiz-option:hover {
        background: rgba(99, 102, 241, 0.15);
        border-color: rgba(99, 102, 241, 0.4);
        transform: translateX(5px);
    }
    
    /* Quiz option selected */
    .quiz-option-selected {
        background: rgba(99, 102, 241, 0.3);
        border-color: rgba(99, 102, 241, 0.6);
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
    
    /* Progress bar styling */
    .stProgress > div > div > div > div {
        background: linear-gradient(135deg, #6366f1, #a855f7);
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
</style>
""", unsafe_allow_html=True)

# Configuration
FLASK_QUIZ_API_URL = "http://localhost:5000/api/generate-quiz"
FLASK_EVAL_API_URL = "http://localhost:5000/api/evaluate-quiz"

# Initialize session state
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
            return {"error": f"API Error: {error_data.get('error', 'Unknown error')}"}
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to Flask server. Please ensure it's running on http://localhost:5000"}
    except requests.exceptions.Timeout:
        return {"error": "Request timed out. The file or video might be too large or processing is taking too long."}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

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
            return {"error": f"API Error: {error_data.get('error', 'Unknown error')}"}
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to Flask server. Please ensure it's running on http://localhost:5000"}
    except requests.exceptions.Timeout:
        return {"error": "Request timed out while evaluating quiz."}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

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

# Sidebar
with st.sidebar:
    st.markdown("<h1 style='color: #6366f1; text-align: center;'>📝 StudyMate Quiz</h1>", unsafe_allow_html=True)
    
    # API Status Check
    try:
        status_response = requests.get("http://localhost:5000", timeout=5)
        st.success("✅ Flask Server Connected")
    except:
        st.error("❌ Flask Server Disconnected")
        st.info("Please start the Flask server:\n```bash\npython app.py\n```")
    
    # Quiz Configuration
    st.markdown("### Quiz Settings")
    
    num_questions = st.selectbox(
        "Number of Questions",
        options=[3, 5, 8, 10, 15, 20],
        index=1,
        key="num_questions"
    )
    
    difficulty = st.selectbox(
        "Difficulty Level",
        options=['easy', 'medium', 'hard'],
        index=1,
        key="difficulty"
    )
    
    st.markdown("---")
    
    # Quiz Stats
    st.markdown("### Quiz Statistics")
    st.metric("Quizzes Taken", len(st.session_state.quiz_history))
    
    if st.session_state.quiz_history:
        avg_score = sum([quiz['score'] for quiz in st.session_state.quiz_history]) / len(st.session_state.quiz_history)
        st.metric("Average Score", f"{avg_score:.1f}%")
        
        best_score = max([quiz['score'] for quiz in st.session_state.quiz_history])
        st.metric("Best Score", f"{best_score:.1f}%")
    
    st.markdown("---")
    
    # Quick Actions
    st.markdown("### Quick Actions")
    if st.button("🔄 Reset Quiz", key="reset_quiz"):
        st.session_state.quiz_data = None
        st.session_state.quiz_id = None
        st.session_state.user_answers = []
        st.session_state.quiz_submitted = False
        st.session_state.quiz_results = None
        st.success("Quiz reset!")
        st.rerun()
    
    if st.button("📊 Clear History", key="clear_quiz_history"):
        st.session_state.quiz_history = []
        st.success("History cleared!")
        st.rerun()

# Main Content Area
st.markdown('<h1 class="main-title">📝 Quiz Center</h1>', unsafe_allow_html=True)

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
                        st.error(f"❌ Error: {result['error']}")
                    else:
                        st.session_state.quiz_data = result
                        st.session_state.quiz_id = result['quiz_id']
                        st.session_state.user_answers = [-1] * len(result['questions'])  # Initialize with -1 (no answer)
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
                        st.error(f"❌ Error: {result['error']}")
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
                        st.error(f"❌ Error: {result['error']}")
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
            index=st.session_state.user_answers[i] if st.session_state.user_answers[i] != -1 else 0
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
                            "source_type": "PDF/Audio/Video"
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
            st.info("Navigate to the Study Center to continue learning!")

# Quiz History Section
if st.session_state.quiz_history:
    st.markdown("---")
    st.markdown("## 📚 Quiz History")
    
    with st.expander(f"View {len(st.session_state.quiz_history)} Previous Quizzes", expanded=False):
        for i, quiz in enumerate(reversed(st.session_state.quiz_history[-10:]), 1):  # Show last 10
            st.markdown('<div class="study-card">', unsafe_allow_html=True)
            st.markdown(f"**Quiz #{len(st.session_state.quiz_history)-i+1}**")
            st.markdown(f"**Score:** {quiz['score']:.1f}%")
            st.markdown(f"**Questions:** {quiz['total_questions']}")
            st.markdown(f"**Difficulty:** {quiz['difficulty'].title()}")
            st.markdown(f"**Date:** {datetime.fromisoformat(quiz['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}")
            st.markdown('</div>', unsafe_allow_html=True)

# Footer Statistics
st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown('<div class="study-card">', unsafe_allow_html=True)
    st.markdown("### 📊 Quiz Statistics")
    st.metric("Total Quizzes", len(st.session_state.quiz_history))
    if st.session_state.quiz_history:
        avg_score = sum([quiz['score'] for quiz in st.session_state.quiz_history]) / len(st.session_state.quiz_history)
        st.metric("Average Score", f"{avg_score:.1f}%")
    else:
        st.metric("Average Score", "N/A")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="study-card">', unsafe_allow_html=True)
    st.markdown("### 🏆 Performance")
    if st.session_state.quiz_history:
        best_score = max([quiz['score'] for quiz in st.session_state.quiz_history])
        worst_score = min([quiz['score'] for quiz in st.session_state.quiz_history])
        st.metric("Best Score", f"{best_score:.1f}%")
        st.metric("Lowest Score", f"{worst_score:.1f}%")
    else:
        st.metric("Best Score", "N/A")
        st.metric("Lowest Score", "N/A")
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="study-card">', unsafe_allow_html=True)
    st.markdown("### 🎯 Study Goals")
    if st.session_state.quiz_history:
        progress = min(100, len(st.session_state.quiz_history) * 10)
        st.progress(progress / 100)
        st.markdown(f"Study Progress: {progress}%")
        
        # Performance trend
        if len(st.session_state.quiz_history) >= 2:
            recent_avg = sum([quiz['score'] for quiz in st.session_state.quiz_history[-3:]]) / min(3, len(st.session_state.quiz_history))
            if recent_avg >= 80:
                st.success("📈 Excellent recent performance!")
            elif recent_avg >= 70:
                st.info("📊 Good recent performance!")
            else:
                st.warning("📚 Keep practicing to improve!")
    else:
        st.progress(0)
        st.markdown("Take your first quiz to start tracking progress!")
    st.markdown('</div>', unsafe_allow_html=True)

# Additional Features Section
st.markdown("---")
st.markdown("## 🚀 Additional Features")

col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="study-card">', unsafe_allow_html=True)
    st.markdown("### 📈 Performance Analytics")
    
    if len(st.session_state.quiz_history) >= 3:
        # Calculate performance by difficulty
        difficulty_stats = {'easy': [], 'medium': [], 'hard': []}
        for quiz in st.session_state.quiz_history:
            if quiz['difficulty'] in difficulty_stats:
                difficulty_stats[quiz['difficulty']].append(quiz['score'])
        
        st.markdown("**Average Scores by Difficulty:**")
        for diff, scores in difficulty_stats.items():
            if scores:
                avg = sum(scores) / len(scores)
                st.markdown(f"- {diff.title()}: {avg:.1f}% ({len(scores)} quizzes)")
        
        # Recent performance trend
        if len(st.session_state.quiz_history) >= 5:
            recent_scores = [quiz['score'] for quiz in st.session_state.quiz_history[-5:]]
            trend = "📈 Improving" if recent_scores[-1] > recent_scores[0] else "📉 Declining" if recent_scores[-1] < recent_scores[0] else "➡️ Stable"
            st.markdown(f"**Recent Trend:** {trend}")
    else:
        st.info("Take more quizzes to see detailed analytics!")
    
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="study-card">', unsafe_allow_html=True)
    st.markdown("### 🎓 Study Recommendations")
    
    if st.session_state.quiz_history:
        latest_score = st.session_state.quiz_history[-1]['score']
        
        if latest_score >= 90:
            st.success("🏆 Excellent work! Try harder difficulty levels to challenge yourself.")
        elif latest_score >= 80:
            st.info("👍 Great job! Consider mixing different difficulty levels.")
        elif latest_score >= 70:
            st.warning("📚 Good progress! Focus on areas where you struggled.")
        else:
            st.error("💪 Keep studying! Review the explanations and try again.")
        
        st.markdown("**Study Tips:**")
        st.markdown("- Review quiz explanations carefully")
        st.markdown("- Take notes on missed questions")
        st.markdown("- Practice regularly with different difficulties")
        st.markdown("- Focus on understanding concepts, not memorization")
    else:
        st.info("📚 Welcome to StudyMate Quiz! Start by taking your first quiz to get personalized recommendations.")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Help Section
st.markdown("---")
st.markdown("## ❓ How to Use")

with st.expander("📖 Quiz Instructions", expanded=False):
    st.markdown("""
    ### Getting Started
    1. **Choose your source:** Upload a PDF, audio file, or paste a YouTube URL
    2. **Configure settings:** Select number of questions (3-20) and difficulty level
    3. **Generate quiz:** Click the generate button and wait for processing
    4. **Take the quiz:** Answer all questions by selecting the best option
    5. **Submit & review:** Submit your answers and review detailed results
    
    ### Difficulty Levels
    - **Easy:** Basic facts and definitions from the content
    - **Medium:** Understanding and application of concepts
    - **Hard:** Analysis, inference, and critical thinking
    
    ### File Requirements
    - **PDF:** Any readable PDF document (max 200MB)
    - **Audio:** MP3 or WAV files (max 200MB)
    - **Video:** Any public YouTube video with available transcripts
    
    ### Tips for Better Results
    - Use clear, well-structured source materials
    - Ensure audio files have good quality and clear speech
    - For videos, choose content with good audio and relevant educational material
    - Review explanations after each quiz to improve understanding
    """)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #6b7280; padding: 2rem;'>"
    "🎓 StudyMate Quiz Center - Enhance your learning with AI-powered assessments<br>"
    "Built with Streamlit & Flask | Powered by Ollama & SentenceTransformers"
    "</div>",
    unsafe_allow_html=True
)