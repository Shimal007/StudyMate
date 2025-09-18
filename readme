StudyMate AI Learning Platform
Welcome to StudyMate, an AI-powered learning platform designed to help you study smarter! Upload PDFs, audio files, or YouTube videos, ask questions, and generate quizzes to test your knowledge. Built with Streamlit for a sleek frontend and Flask for a robust backend, StudyMate makes learning interactive and engaging.
🌟 Features

Study Center:

Upload PDFs or audio files (MP3/WAV) or input YouTube URLs.
Ask questions about your content and get AI-generated answers.
Download Q&A sessions as PDF reports.


Quiz Center:

Generate customizable quizzes from your uploaded materials.
Choose the number of questions (3–20) and difficulty (Easy, Medium, Hard).
Review detailed results with explanations and download them as PDFs.


Analytics Dashboard:

Track your study progress and quiz performance.
View stats like total questions asked, quizzes taken, and average scores.


Settings & Help:

Clear study or quiz data with one click.
Access a user guide and system requirements.
Export your complete Q&A history as a PDF.



🚀 Getting Started
Follow these steps to set up and run StudyMate on your local machine.
Prerequisites

Python 3.8+: Ensure Python is installed. Download Python.
Ollama: Used for AI model inference. Install Ollama.
Node.js: Required for some dependencies (optional for development).
A modern web browser (Chrome, Firefox, etc.).

Installation

Clone the Repository:
git clone https://github.com/your-repo/studymate.git
cd studymate


Set Up a Virtual Environment (recommended):
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate


Install Python Dependencies:Install the required packages for both frontend and backend:
pip install -r requirements.txt

Example requirements.txt:
streamlit==1.38.0
flask==2.3.3
flask-cors==4.0.1
requests==2.32.3
PyMuPDF==1.24.9
sentence-transformers==3.1.0
faiss-cpu==1.8.0
speechrecognition==3.10.4
pydub==0.25.1
youtube-transcript-api==0.6.2
reportlab==4.2.2


Set Up Ollama:

Start the Ollama server:ollama serve


Pull the required model (e.g., ibm/granite3.3:2b):ollama pull ibm/granite3.3:2b




Run the Backend:Start the Flask server (app.py):
python app.py

The server will run at http://localhost:5000.

Run the Frontend:Start the Streamlit app (gpu.py):
streamlit run gpu.py

Open your browser and navigate to http://localhost:8501.


📚 Usage Guide
Study Center

Choose a tab: PDF Study, Audio Study, or Video Study.
Upload a PDF/audio file or enter a YouTube URL.
Ask a question about the content and click Ask Question.
View answers and download your Q&A history as a PDF.

Quiz Center

Select a tab: PDF Quiz, Audio Quiz, or Video Quiz.
Upload a file or enter a YouTube URL.
Configure the quiz (number of questions and difficulty) in the sidebar.
Click Generate Questions, answer the quiz, and submit.
Review results and download them as a PDF.

Analytics

Check your study stats (sources processed, questions asked).
Review quiz performance (average score, best score, difficulty breakdown).

Settings

Clear study or quiz data.
Export Q&A history.
Read the user guide for tips.

🛠️ Troubleshooting

Flask Server Disconnected:

Ensure app.py is running (python app.py).
Check if http://localhost:5000 is accessible.


Ollama Errors:

Verify the Ollama server is running (ollama serve).
Confirm the model (ibm/granite3.3:2b) is pulled.


File Upload Issues:

Ensure files are under 200MB.
Only use supported formats: PDF, MP3/WAV, or valid YouTube URLs.


JSON Parsing Errors:

If you see "Failed to parse JSON" errors, check the server logs for details (app.py logs the request_id).
Ensure the Ollama model is correctly configured.


Slow Processing:

Large files or videos may take time to process. Be patient or try smaller files.



📝 Notes

File Limits: Maximum file size is 200MB for PDFs and audio.
YouTube Transcripts: Only videos with English transcripts are supported.
Browser Compatibility: Use a modern browser with JavaScript enabled.
Error Debugging: Check the request_id in error messages to trace issues in server logs.

🤝 Contributing
We welcome contributions! To contribute:

Fork the repository.
Create a feature branch (git checkout -b feature/your-feature).
Commit your changes (git commit -m "Add your feature").
Push to the branch (git push origin feature/your-feature).
Open a Pull Request.

📜 License
This project is licensed under the MIT License. See the LICENSE file for details.
🙌 Acknowledgments

Built with Streamlit, Flask, and Ollama.
Powered by SentenceTransformers and FAISS.
Thanks to the open-source community for their amazing tools!


StudyMate - Learn smarter, not harder! 🎓
