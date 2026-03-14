"""File handling module for resume processing system.

Handles file validation, ZIP extraction, Google Drive integration,
and in-memory file processing without local storage.
"""

import os
import zipfile
import logging
import io
from pathlib import Path
from typing import List, Optional, Tuple
from urllib.parse import urlparse, parse_qs
import re

from config import LOGS_FOLDER

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler(os.path.join(LOGS_FOLDER, 'file_handler.log'))
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def validate_file_format(filename: str) -> bool:
    """Check if file has a supported format (PDF or DOCX).
    
    Args:
        filename: Name of the file to validate
        
    Returns:
        True if file format is supported, False otherwise
    """
    if not filename:
        return False
    
    file_ext = Path(filename).suffix.lower()
    return file_ext in {'.pdf', '.docx'}


def extract_zip_in_memory(file_obj) -> List[Tuple[str, bytes]]:
    """Extract files from ZIP archive in memory without storing locally.
    
    Args:
        file_obj: File object from Flask request (ZIP file)
        
    Returns:
        List of tuples (filename, file_content) for all files in ZIP
        
    Raises:
        ValueError: If file is not a valid ZIP archive
    """
    try:
        # Read file into memory
        file_obj.seek(0)
        zip_bytes = file_obj.read()
        
        if not zip_bytes:
            raise ValueError("ZIP file is empty")
        
        # Open ZIP from bytes
        zip_buffer = io.BytesIO(zip_bytes)
        
        if not zipfile.is_zipfile(zip_buffer):
            raise ValueError("Uploaded file is not a valid ZIP archive")
        
        extracted_files = []
        
        with zipfile.ZipFile(zip_buffer, 'r') as zip_ref:
            file_list = zip_ref.namelist()
            
            if not file_list:
                logger.warning("ZIP file is empty")
                return []
            
            # Extract files into memory
            for file_name in file_list:
                # Skip directories
                if file_name.endswith('/'):
                    continue
                
                # Read file content into memory
                file_content = zip_ref.read(file_name)
                
                # Filter only PDF and DOCX files
                if validate_file_format(file_name):
                    extracted_files.append((file_name, file_content))
        
        logger.info(f"Successfully extracted {len(extracted_files)} resume files from ZIP")
        return extracted_files
        
    except zipfile.BadZipFile as e:
        logger.error(f"Bad ZIP file: {str(e)}")
        raise ValueError("ZIP file is corrupted or invalid")
    except Exception as e:
        logger.error(f"ZIP extraction failed: {str(e)}")
        raise IOError(f"Failed to extract ZIP file: {str(e)}")


def extract_folder_id(drive_link: str) -> str:
    """Extract folder ID from various Google Drive link formats.
    
    Supports multiple Google Drive link formats:
    - https://drive.google.com/drive/folders/FOLDER_ID
    - https://drive.google.com/drive/folders/FOLDER_ID?usp=sharing
    - https://drive.google.com/open?id=FOLDER_ID
    
    Args:
        drive_link: Google Drive folder link
        
    Returns:
        Extracted folder ID
        
    Raises:
        ValueError: If link is invalid or folder ID cannot be extracted
    """
    try:
        from google_drive_public import extract_folder_id as extract_id_public
        return extract_id_public(drive_link)
    except ImportError:
        logger.error("google_drive_public module not found")
        raise ValueError("Google Drive public module not found.")
    except Exception as e:
        logger.error(f"Failed to extract folder ID: {str(e)}")
        raise ValueError(str(e))



def download_from_drive(folder_id: str, credentials=None) -> List[Tuple[str, bytes]]:
    """Download files from Google Drive folder into memory.
    
    Uses the Google Drive REST API v3 with an API key.
    
    Args:
        folder_id: Google Drive folder ID
        credentials: Deprecated (kept for backward compatibility, not used)
        
    Returns:
        List of tuples (filename, file_content) for downloaded files
        
    Raises:
        ValueError: If folder_id is invalid or API key is missing
        IOError: If download fails
    """
    if not folder_id:
        raise ValueError("Folder ID is required")
    
    logger.info("Using Google Drive REST API with API key")
    
    try:
        from google_drive_public import download_from_public_folder
        from config import GOOGLE_DRIVE_API_KEY
        
        # Download files using Google Drive API
        downloaded_files = download_from_public_folder(folder_id, GOOGLE_DRIVE_API_KEY)
        
        logger.info(f"Successfully downloaded {len(downloaded_files)} files from Google Drive")
        return downloaded_files
        
    except ImportError as e:
        logger.error(f"Import error: {str(e)}")
        raise IOError("Required modules not found.")
    except ValueError as e:
        logger.error(f"Configuration error: {str(e)}")
        raise IOError(str(e))
    except Exception as e:
        logger.error(f"Failed to download files from Google Drive: {str(e)}")
        raise IOError(f"Failed to download files from Google Drive: {str(e)}")


def cleanup_temp_files(folder_path: str) -> None:
    """Placeholder for cleanup - no longer needed with in-memory processing."""
    pass
