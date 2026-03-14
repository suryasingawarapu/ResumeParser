# Setup Instructions

## Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

## Step 2: Download spaCy Model
```bash
python -m spacy download en_core_web_sm
```

## Step 3: Get Google Drive API Key

1. Go to: https://console.cloud.google.com/
2. Create a new project: "Resume Parser"
3. Search for "Google Drive API"
4. Click "ENABLE"
5. Click "Create Credentials" → "API Key"
6. Copy the API key

## Step 4: Edit .env File

Open `.env` and replace `PASTE_YOUR_API_KEY_HERE` with your API key:

```
DEBUG=False
SECRET_KEY=resume-parser-secret-key-2024
GOOGLE_DRIVE_API_KEY=AIzaSyD_1234567890abcdefghijklmnopqrstuvwxyz
```

## Step 5: Run Application
```bash
python app.py
```

## Step 6: Open in Browser
```
http://localhost:5000
```

## Done!

Your resume parser is now ready to use.
