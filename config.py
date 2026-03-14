import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent

# Upload folder configuration
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
ZIP_EXTRACTED_FOLDER = os.path.join(BASE_DIR, 'zip_extracted')
DRIVE_DOWNLOADS_FOLDER = os.path.join(BASE_DIR, 'drive_downloads')
LOGS_FOLDER = os.path.join(BASE_DIR, 'logs')

# File size limits (in bytes)
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB

# Supported file formats
SUPPORTED_FORMATS = {'.pdf', '.docx'}

# Flask configuration
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')

# Google Drive configuration
GOOGLE_DRIVE_API_KEY = os.getenv('GOOGLE_DRIVE_API_KEY', '')

# Tesseract OCR configuration (for scanned PDFs)
try:
    import pytesseract
    # Windows: Configure Tesseract path if needed
    # Uncomment and modify if Tesseract is not in system PATH
    # pytesseract.pytesseract.pytesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
except ImportError:
    pass

# Ensure all required folders exist
for folder in [UPLOAD_FOLDER, ZIP_EXTRACTED_FOLDER, DRIVE_DOWNLOADS_FOLDER, LOGS_FOLDER]:
    os.makedirs(folder, exist_ok=True)
