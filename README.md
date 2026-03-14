# Resume Parser

A Flask-based resume processing system that extracts candidate information (name, email, phone) from multiple resume sources.

## Features

- Single resume file upload (PDF/DOCX)
- ZIP file batch processing
- Google Drive folder integration
- Email-based deduplication
- Resume parsing with name, email, and phone extraction
- HTML results table display

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Download spaCy Model
```bash
python -m spacy download en_core_web_sm
```

### 3. Setup Google Drive API Key

1. Go to: https://console.cloud.google.com/
2. Create a new project
3. Enable "Google Drive API"
4. Create an API Key
5. Copy the API key

### 4. Configure .env File

Edit `.env` and replace `PASTE_YOUR_API_KEY_HERE` with your actual API key:

```
DEBUG=False
SECRET_KEY=resume-parser-secret-key-2024
GOOGLE_DRIVE_API_KEY=YOUR_API_KEY_HERE
```

### 5. Run the Application
```bash
python app.py
```

Open browser to: http://localhost:5000

## Usage

### Single Resume Upload
1. Click "Upload Single Resume"
2. Select a PDF or DOCX file
3. Click "Upload"

### ZIP File Upload
1. Click "Upload ZIP File"
2. Select a ZIP containing resumes
3. Click "Upload"

### Google Drive Folder
1. Click "Google Drive Folder"
2. Paste a Google Drive folder link
3. Click "Process"

## Supported Formats
- PDF (.pdf)
- DOCX (.docx)

## Project Structure
```
.
├── .env                   # Environment variables (create this)
├── app.py                 # Flask application
├── parser_robust.py       # Resume parsing logic
├── file_handler.py        # File handling utilities
├── google_drive_public.py # Google Drive API handler
├── deduplication.py       # Duplicate detection
├── result_manager.py      # Results formatting
├── config.py              # Configuration
├── requirements.txt       # Dependencies
├── templates/
│   └── index.html         # Web interface
└── static/
    ├── css/
    │   └── style.css      # Styling
    └── js/
        └── app.js         # Frontend logic
```

## Environment Variables

- `DEBUG` - Debug mode (True/False)
- `SECRET_KEY` - Flask secret key
- `GOOGLE_DRIVE_API_KEY` - Google Drive API key

## Logging

Logs are stored in `logs/` directory:
- `errors.log` - Error logs
- `file_handler.log` - File handling logs
