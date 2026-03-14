"""Google Drive folder handler using REST API with API key.

Handles downloading files from Google Drive folders
using the Google Drive REST API v3 with an API key.
"""

import logging
import re
import requests
import io
from typing import List, Tuple
from pathlib import Path
import os

logger = logging.getLogger(__name__)

# Google Drive API endpoints
GOOGLE_DRIVE_API_URL = "https://www.googleapis.com/drive/v3/files"
GOOGLE_DRIVE_DOWNLOAD_URL = "https://www.googleapis.com/drive/v3/files"

# Supported file extensions
SUPPORTED_EXTENSIONS = {'.pdf', '.docx'}

# Get API key from environment
GOOGLE_DRIVE_API_KEY = os.getenv('GOOGLE_DRIVE_API_KEY', '')


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
    if not drive_link or not isinstance(drive_link, str):
        raise ValueError("Invalid Google Drive link: link must be a non-empty string")
    
    drive_link = drive_link.strip()
    
    # Pattern 1: /drive/folders/FOLDER_ID
    match = re.search(r'/drive/folders/([a-zA-Z0-9-_]+)', drive_link)
    if match:
        folder_id = match.group(1)
        if _validate_folder_id(folder_id):
            logger.info(f"Extracted folder ID from /drive/folders/ format: {folder_id}")
            return folder_id
    
    # Pattern 2: ?id=FOLDER_ID
    match = re.search(r'[?&]id=([a-zA-Z0-9-_]+)', drive_link)
    if match:
        folder_id = match.group(1)
        if _validate_folder_id(folder_id):
            logger.info(f"Extracted folder ID from ?id= format: {folder_id}")
            return folder_id
    
    logger.error(f"Could not extract folder ID from link: {drive_link}")
    raise ValueError("Invalid Google Drive link format. Please provide a valid folder link.")


def _validate_folder_id(folder_id: str) -> bool:
    """Validate Google Drive folder ID format.
    
    Args:
        folder_id: Folder ID to validate
        
    Returns:
        True if folder ID format is valid, False otherwise
    """
    # Google Drive folder IDs are typically 33 characters of alphanumeric, dash, underscore
    if not folder_id or len(folder_id) < 20:
        logger.debug(f"Folder ID too short: {len(folder_id)} chars")
        return False
    
    if not re.match(r'^[a-zA-Z0-9-_]+$', folder_id):
        logger.debug(f"Folder ID contains invalid characters")
        return False
    
    return True


def _validate_file_format(filename: str) -> bool:
    """Check if file has a supported format (PDF or DOCX).
    
    Args:
        filename: Name of the file to validate
        
    Returns:
        True if file format is supported, False otherwise
    """
    if not filename:
        return False
    
    file_ext = Path(filename).suffix.lower()
    return file_ext in SUPPORTED_EXTENSIONS


def download_from_public_folder(folder_id: str, api_key: str = None) -> List[Tuple[str, bytes]]:
    """Download files from Google Drive folder using REST API.
    
    Uses the Google Drive REST API v3 with an API key.
    Works with any folder accessible via the API key.
    
    Args:
        folder_id: Google Drive folder ID
        api_key: Google Drive API key (uses environment variable if not provided)
        
    Returns:
        List of tuples (filename, file_content) for downloaded files
        
    Raises:
        ValueError: If folder_id is invalid or API key is missing
        IOError: If download fails
    """
    if not folder_id:
        raise ValueError("Folder ID is required")
    
    # Use provided API key or get from environment
    if not api_key:
        api_key = GOOGLE_DRIVE_API_KEY
    
    if not api_key:
        logger.error("Google Drive API key not provided")
        raise ValueError("Google Drive API key is required. Please set GOOGLE_DRIVE_API_KEY environment variable.")
    
    logger.info(f"Downloading files from Google Drive folder: {folder_id}")
    logger.debug(f"Using Google Drive API key: {api_key[:10]}...")
    
    try:
        downloaded_files = []
        
        # Build query to list files in folder
        query = f"'{folder_id}' in parents and trashed=false"
        
        # Build request parameters
        params = {
            'q': query,
            'spaces': 'drive',
            'fields': 'files(id, name, mimeType, size)',
            'pageSize': 1000,
            'key': api_key
        }
        
        # List files in folder
        logger.debug(f"Querying Google Drive API: {query}")
        response = requests.get(GOOGLE_DRIVE_API_URL, params=params, timeout=30)
        
        logger.debug(f"Google Drive API response status: {response.status_code}")
        
        if response.status_code == 403:
            logger.error("Access denied to Google Drive folder (403 Forbidden)")
            raise IOError("Access denied to Google Drive folder. Check API key permissions and folder access.")
        
        if response.status_code == 404:
            logger.error("Google Drive folder not found (404)")
            raise IOError("Google Drive folder not found. Please check the folder ID.")
        
        if response.status_code == 400:
            logger.error(f"Bad request to Google Drive API: {response.text}")
            raise IOError(f"Invalid request to Google Drive API: {response.text}")
        
        if response.status_code != 200:
            logger.error(f"Google Drive API error: {response.status_code} - {response.text}")
            raise IOError(f"Google Drive API error: {response.status_code}")
        
        data = response.json()
        files = data.get('files', [])
        
        if not files:
            logger.warning(f"No files found in Google Drive folder: {folder_id}")
            return []
        
        logger.info(f"Found {len(files)} files in folder, filtering for resumes...")
        
        # Download each file
        for file in files:
            # Skip folders
            if file['mimeType'] == 'application/vnd.google-apps.folder':
                logger.debug(f"Skipping folder: {file['name']}")
                continue
            
            file_name = file['name']
            file_id = file['id']
            file_size = file.get('size', 0)
            
            # Filter only PDF and DOCX files
            if not _validate_file_format(file_name):
                logger.debug(f"Skipping unsupported file: {file_name}")
                continue
            
            try:
                logger.info(f"Downloading file: {file_name} ({file_size} bytes)")
                
                # Download file from Google Drive using direct download URL
                # This uses the alt=media parameter to get the file content
                download_url = f"{GOOGLE_DRIVE_DOWNLOAD_URL}/{file_id}?alt=media&key={api_key}"
                
                file_response = requests.get(download_url, timeout=60)
                
                if file_response.status_code == 403:
                    logger.warning(f"Access denied downloading {file_name}")
                    continue
                
                if file_response.status_code == 404:
                    logger.warning(f"File not found: {file_name}")
                    continue
                
                if file_response.status_code != 200:
                    logger.warning(f"Failed to download {file_name}: HTTP {file_response.status_code}")
                    continue
                
                file_content = file_response.content
                
                if not file_content:
                    logger.warning(f"Downloaded file is empty: {file_name}")
                    continue
                
                downloaded_files.append((file_name, file_content))
                logger.info(f"Successfully downloaded: {file_name} ({len(file_content)} bytes)")
                
            except requests.Timeout:
                logger.error(f"Timeout downloading file: {file_name}")
                continue
            except Exception as e:
                logger.error(f"Failed to download file {file_name}: {str(e)}")
                continue
        
        logger.info(f"Successfully downloaded {len(downloaded_files)} resume files from Google Drive")
        return downloaded_files
        
    except requests.RequestException as e:
        logger.error(f"Network error accessing Google Drive: {str(e)}")
        raise IOError(f"Network error accessing Google Drive: {str(e)}")
    except ValueError as e:
        logger.error(f"Invalid configuration: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Failed to download files from Google Drive: {str(e)}")
        raise IOError(f"Failed to download files from Google Drive: {str(e)}")
