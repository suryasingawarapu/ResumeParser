"""Result Manager Module for formatting and managing processing results."""

import json
import logging
import os
import shutil
from typing import Dict, List, Any
from datetime import datetime
from pathlib import Path
import html

from config import LOGS_FOLDER

# Configure logging
logger = logging.getLogger(__name__)


def generate_html_table(candidates: List[Dict]) -> str:
    """
    Generate an HTML table from candidate data.
    
    Creates a valid HTML table with proper structure (thead, tbody, tr, td)
    including columns for Name, Email, and Phone. Includes one row per candidate.
    Properly escapes HTML special characters to prevent injection.
    
    Args:
        candidates: List of candidate dictionaries with 'name', 'email', 'phone' fields
        
    Returns:
        HTML string representing a table with all candidates
        
    Requirements: 7.1, 7.2, 7.3
    """
    # Start building the HTML table
    html_parts = ['<table class="results-table">', '<thead>', '<tr>']
    
    # Add table headers
    headers = ['Name', 'Email', 'Phone']
    for header in headers:
        html_parts.append(f'<th>{html.escape(header)}</th>')
    
    html_parts.append('</tr>')
    html_parts.append('</thead>')
    html_parts.append('<tbody>')
    
    # Add table rows for each candidate
    for candidate in candidates:
        html_parts.append('<tr>')
        
        # Extract and escape candidate data
        name = html.escape(candidate.get('name', ''))
        email = html.escape(candidate.get('email', ''))
        phone = html.escape(candidate.get('phone', ''))
        
        html_parts.append(f'<td>{name}</td>')
        html_parts.append(f'<td>{email}</td>')
        html_parts.append(f'<td>{phone}</td>')
        
        html_parts.append('</tr>')
    
    html_parts.append('</tbody>')
    html_parts.append('</table>')
    
    return '\n'.join(html_parts)


def format_results_json(candidates: List[Dict], 
                       total_files_processed: int = 0,
                       duplicates_removed: int = 0,
                       errors: List[str] = None) -> str:
    """
    Format candidates and metadata as a JSON string.
    
    Creates a JSON array with candidate data and includes metadata about
    the processing operation (total files processed, duplicates removed, errors).
    
    Args:
        candidates: List of candidate dictionaries with 'name', 'email', 'phone' fields
        total_files_processed: Total number of files processed
        duplicates_removed: Number of duplicate candidates removed
        errors: List of error messages encountered during processing
        
    Returns:
        Valid JSON string with candidates and metadata
        
    Requirements: 5.1, 5.2, 5.3
    """
    if errors is None:
        errors = []
    
    # Build the result structure
    result = {
        'candidates': candidates,
        'metadata': {
            'total_files_processed': total_files_processed,
            'duplicates_removed': duplicates_removed,
            'total_candidates': len(candidates),
            'errors': errors
        }
    }
    
    return json.dumps(result, indent=2)


def log_error(error_msg: str, context: str, 
              error_type: str = 'ProcessingError',
              file_name: str = '',
              severity: str = 'error') -> None:
    """
    Log an error with timestamp and context information.
    
    Creates a log entry with error type, file name, message, and severity level.
    Logs are stored in the logs/ folder with timestamp.
    
    Args:
        error_msg: The error message to log
        context: Context where the error occurred (e.g., 'zip_extraction', 'parsing')
        error_type: Type of error (e.g., 'ParseError', 'ValidationError')
        file_name: Name of the file that caused the error (optional)
        severity: Severity level ('debug', 'info', 'warning', 'error', 'critical')
        
    Requirements: 10.1, 10.3
    """
    # Ensure logs folder exists
    os.makedirs(LOGS_FOLDER, exist_ok=True)
    
    # Create error log entry
    error_entry = {
        'timestamp': datetime.now().isoformat(),
        'error_type': error_type,
        'file': file_name,
        'message': error_msg,
        'context': context,
        'severity': severity
    }
    
    # Log to application logger
    log_level = getattr(logging, severity.upper(), logging.ERROR)
    logger.log(log_level, f"[{error_type}] {error_msg} (context: {context})")
    
    # Write to error log file
    try:
        log_file = os.path.join(LOGS_FOLDER, 'errors.log')
        with open(log_file, 'a') as f:
            f.write(json.dumps(error_entry) + '\n')
    except Exception as e:
        logger.error(f"Failed to write to error log: {str(e)}")


def cleanup_temp_files(folder_path: str) -> None:
    """
    Delete temporary files from a specified folder after processing.
    
    Cleans up uploads/, zip_extracted/, and drive_downloads/ folders.
    Handles cleanup errors gracefully without raising exceptions.
    
    Args:
        folder_path: Path to the folder to clean up
        
    Requirements: 9.1, 9.2, 9.3
    """
    try:
        if not os.path.exists(folder_path):
            logger.debug(f"Folder does not exist, skipping cleanup: {folder_path}")
            return
        
        # Remove all files and subdirectories in the folder
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                    logger.debug(f"Deleted file: {file_path}")
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                    logger.debug(f"Deleted directory: {file_path}")
            except Exception as e:
                logger.warning(f"Failed to delete {file_path}: {str(e)}")
                # Continue cleanup even if one file fails
                continue
        
        logger.info(f"Cleanup completed for folder: {folder_path}")
        
    except Exception as e:
        # Handle cleanup errors gracefully
        logger.warning(f"Error during cleanup of {folder_path}: {str(e)}")
