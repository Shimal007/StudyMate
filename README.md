# StudyMate

AI-powered study companion that lets you ask questions about your PDFs, audio files, and YouTube videos.

## What it does

- Upload PDF files and ask questions about them
- Upload audio files (MP3/WAV) and get answers about the content
- Paste YouTube URLs and chat about the video content
- Generate quizzes from your materials
- Create study plans
- Export your Q&A sessions as PDF reports

## Quick Setup

1. Clone the repo
```bash
git clone https://github.com/yourusername/studymate.git
cd studymate
```

2. Install requirements
```bash
pip install -r requirements.txt
```

3. Install Ollama and pull the model
```bash
# Install from https://ollama.ai
ollama pull ibm/granite3.3:2b
ollama serve
```

4. Start the servers
```bash
# Terminal 1: Backend
python backend/app.py

# Terminal 2: Frontend
streamlit run gpu.py
```

5. Open http://localhost:8501 in your browser

## How to use

1. **Upload a file** - PDF document or audio file (MP3/WAV)
2. **Or paste YouTube URL** - Any YouTube video with captions
3. **Ask questions** - Type your question about the content
4. **Get AI answers** - Powered by local AI model
5. **Generate quizzes** - Test yourself on the material
6. **Download reports** - Export your Q&A sessions

## API Endpoints

- `POST /api/answer-question` - Ask questions about uploaded content
- `POST /api/generate-quiz` - Create quizzes
- `POST /api/generate-study-plan` - Make study schedules
- `GET /api/health` - Check if server is running

## Example API call
```bash
curl -X POST http://localhost:5000/api/answer-question \
  -F "file=@mydocument.pdf" \
  -F "question=What is this document about?"
```

## File Structure
```
studymate/
├── backend/app.py          # Flask API server
├── gpu.py                  # Streamlit web interface
└── requirements.txt        # Python packages
```

## Requirements

- Python 3.8+
- Ollama (for AI model)
- 4GB+ RAM

## Supported Files

- **Documents**: PDF files
- **Audio**: MP3, WAV files  
- **Video**: YouTube URLs

## Troubleshooting

**Can't connect to API?**
- Make sure Flask server is running on port 5000
- Check if Ollama is running: `ollama serve`

**File won't upload?**
- Check file size (max 200MB)
- Make sure it's PDF, MP3, or WAV format

**Slow responses?**
- Large files take longer to process
- Audio transcription can be slow


## Contributing

1. Fork the repo
2. Make your changes
3. Test them
4. Submit a pull request
