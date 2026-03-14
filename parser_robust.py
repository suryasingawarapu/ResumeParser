"""Robust resume parser with multiple fallback methods - NO pyresparser dependency."""

import logging
import re
import tempfile
import os
from typing import Dict, Any, Tuple, List
from pathlib import Path

logger = logging.getLogger(__name__)

# Regex patterns
EMAIL_PATTERN = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
PHONE_PATTERN = r'(?:\+\d{1,3}[-.\s]?)?\(?(?:\d{3})\)?[-.\s]?(?:\d{3})[-.\s]?(?:\d{4})\b'
NAME_PATTERN = r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'


def extract_text_from_pdf_pymupdf(file_path: str) -> str:
    """Extract text from PDF using PyMuPDF (fitz)."""
    try:
        import fitz
        text = ""
        with fitz.open(file_path) as doc:
            for page in doc:
                text += page.get_text()
        logger.debug(f"PyMuPDF: Extracted {len(text)} characters")
        return text
    except Exception as e:
        logger.debug(f"PyMuPDF extraction failed: {str(e)}")
        return ""


def extract_text_from_pdf_pypdf2(file_path: str) -> str:
    """Extract text from PDF using PyPDF2."""
    try:
        import PyPDF2
        text = ""
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text()
        logger.debug(f"PyPDF2: Extracted {len(text)} characters")
        return text
    except Exception as e:
        logger.debug(f"PyPDF2 extraction failed: {str(e)}")
        return ""


def extract_text_from_pdf_pdfplumber(file_path: str) -> str:
    """Extract text from PDF using pdfplumber."""
    try:
        import pdfplumber
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
        logger.debug(f"pdfplumber: Extracted {len(text)} characters")
        return text
    except Exception as e:
        logger.debug(f"pdfplumber extraction failed: {str(e)}")
        return ""


def extract_text_from_pdf_pdfminer(file_path: str) -> str:
    """Extract text from PDF using pdfminer (more reliable for complex PDFs)."""
    try:
        from pdfminer.high_level import extract_text
        text = extract_text(file_path)
        logger.debug(f"pdfminer: Extracted {len(text)} characters")
        return text
    except Exception as e:
        logger.debug(f"pdfminer extraction failed: {str(e)}")
        return ""


def extract_text_from_pdf_ocr(file_path: str) -> str:
    """Extract text from PDF using OCR (Tesseract)."""
    try:
        import pytesseract
        from pdf2image import convert_from_path
        
        logger.info("Attempting OCR extraction")
        images = convert_from_path(file_path)
        text = ""
        for image in images:
            text += pytesseract.image_to_string(image) + "\n"
        return text
    except Exception as e:
        logger.debug(f"OCR extraction failed: {str(e)}")
        return ""


def extract_text_from_docx(file_path: str) -> str:
    """Extract text from DOCX file."""
    try:
        from docx import Document
        doc = Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text
    except Exception as e:
        logger.debug(f"DOCX extraction failed: {str(e)}")
        return ""


def extract_text_from_file(file_path: str) -> str:
    """
    Extract text from file using multiple methods in order of preference.
    
    Tries:
    1. PyMuPDF (fastest, most reliable)
    2. PyPDF2 (good for searchable PDFs)
    3. pdfplumber (handles complex PDFs)
    4. pdfminer (more reliable for difficult PDFs)
    5. OCR (for scanned images)
    6. DOCX extraction (for Word documents)
    """
    file_ext = Path(file_path).suffix.lower()
    
    logger.info(f"Extracting text from {file_path} (ext: {file_ext})")
    
    # Try PDF extraction methods
    if file_ext == '.pdf':
        # Method 1: PyMuPDF (fastest)
        logger.debug("Trying PyMuPDF extraction...")
        text = extract_text_from_pdf_pymupdf(file_path)
        if text.strip():
            logger.info(f"SUCCESS: Text extracted via PyMuPDF: {len(text)} chars")
            return text
        logger.debug("PyMuPDF returned empty text")
        
        # Method 2: PyPDF2
        logger.debug("Trying PyPDF2 extraction...")
        text = extract_text_from_pdf_pypdf2(file_path)
        if text.strip():
            logger.info(f"SUCCESS: Text extracted via PyPDF2: {len(text)} chars")
            return text
        logger.debug("PyPDF2 returned empty text")
        
        # Method 3: pdfplumber
        logger.debug("Trying pdfplumber extraction...")
        text = extract_text_from_pdf_pdfplumber(file_path)
        if text.strip():
            logger.info(f"SUCCESS: Text extracted via pdfplumber: {len(text)} chars")
            return text
        logger.debug("pdfplumber returned empty text")
        
        # Method 4: pdfminer
        logger.debug("Trying pdfminer extraction...")
        text = extract_text_from_pdf_pdfminer(file_path)
        if text.strip():
            logger.info(f"SUCCESS: Text extracted via pdfminer: {len(text)} chars")
            return text
        logger.debug("pdfminer returned empty text")
        
        # Method 5: OCR (for scanned images)
        logger.debug("Trying OCR extraction...")
        text = extract_text_from_pdf_ocr(file_path)
        if text.strip():
            logger.info(f"SUCCESS: Text extracted via OCR: {len(text)} chars")
            return text
        logger.debug("OCR returned empty text")
    
    # Try DOCX extraction
    elif file_ext == '.docx':
        logger.debug("Trying DOCX extraction...")
        text = extract_text_from_docx(file_path)
        if text.strip():
            logger.info(f"SUCCESS: Text extracted from DOCX: {len(text)} chars")
            return text
        logger.debug("DOCX extraction returned empty text")
    
    logger.warning(f"FAILED: Could not extract text from {file_path}")
    return ""


def extract_email(text: str) -> str:
    """Extract email from text using regex."""
    if not text:
        logger.debug("extract_email: No text provided")
        return ""
    
    emails = re.findall(EMAIL_PATTERN, text)
    if emails:
        logger.info(f"Email found: {emails[0]}")
        return emails[0]
    
    logger.debug(f"No email found in text (searched {len(text)} chars)")
    return ""


def extract_phone(text: str) -> str:
    """Extract phone number from text using regex."""
    if not text:
        return ""
    
    phones = re.findall(PHONE_PATTERN, text)
    if phones:
        logger.info(f"Phone found: {phones[0]}")
        return phones[0]
    
    return ""


def extract_name(text: str) -> str:
    """Extract name from text (usually first line or before email)."""
    if not text:
        return ""
    
    lines = text.split('\n')
    
    # Try first non-empty line
    for line in lines:
        line = line.strip()
        if line and len(line) > 2:
            # Remove email if present
            line = re.sub(EMAIL_PATTERN, '', line).strip()
            # Remove phone if present
            line = re.sub(PHONE_PATTERN, '', line).strip()
            
            if line and len(line) > 2:
                logger.info(f"Name extracted: {line}")
                return line
    
    return ""


def parse_resume_from_bytes(filename: str, file_content: bytes) -> Dict[str, Any]:
    """
    Parse resume from bytes without storing locally.
    
    Uses robust text extraction with multiple fallback methods.
    No dependency on pyresparser.
    
    Args:
        filename: Name of resume file
        file_content: Binary content
        
    Returns:
        Dictionary with name, email, phone
    """
    temp_file = None
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(filename).suffix) as tmp:
            tmp.write(file_content)
            temp_file = tmp.name
        
        logger.info(f"Parsing resume: {filename} ({len(file_content)} bytes)")
        
        # Extract text using robust methods
        text = extract_text_from_file(temp_file)
        
        if not text.strip():
            logger.warning(f"No text extracted from {filename} - returning empty candidate")
            return {'name': '', 'email': '', 'phone': ''}
        
        # Extract fields
        name = extract_name(text)
        email = extract_email(text)
        phone = extract_phone(text)
        
        candidate_info = {
            'name': name,
            'email': email,
            'phone': phone
        }
        
        logger.info(f"Parsed {filename}: name='{name}', email='{email}', phone='{phone}'")
        
        return candidate_info
        
    except Exception as e:
        logger.error(f"Failed to parse {filename}: {str(e)}", exc_info=True)
        return {'name': '', 'email': '', 'phone': ''}
    finally:
        # Cleanup
        if temp_file and os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except:
                pass


def process_resume_batch_from_bytes(files: List[Tuple[str, bytes]]) -> List[Dict]:
    """Process multiple resume files from bytes."""
    candidates = []
    
    for filename, file_content in files:
        try:
            candidate = parse_resume_from_bytes(filename, file_content)
            candidates.append(candidate)
        except Exception as e:
            logger.error(f"Error processing {filename}: {str(e)}")
            continue
    
    return candidates
