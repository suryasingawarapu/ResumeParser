"""Resume parsing module - uses robust parser without pyresparser dependency."""

import logging
from typing import Dict, List, Any, Tuple

# Import robust parser
from parser_robust import (
    parse_resume_from_bytes,
    process_resume_batch_from_bytes
)

# Configure logging
logger = logging.getLogger(__name__)

# Re-export functions for compatibility
__all__ = [
    'parse_resume_from_bytes',
    'process_resume_batch_from_bytes',
    'parse_resume',
    'process_resume_batch',
    'format_as_json'
]


def parse_resume(file_path: str) -> Dict[str, Any]:
    """
    Parse a resume file.
    
    Args:
        file_path: Path to resume file
        
    Returns:
        Dictionary with name, email, phone
    """
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
        return parse_resume_from_bytes(file_path, content)
    except Exception as e:
        logger.error(f"Failed to parse {file_path}: {str(e)}")
        return {'name': '', 'email': '', 'phone': ''}


def process_resume_batch(file_paths: List[str]) -> List[Dict]:
    """
    Process multiple resume files.
    
    Args:
        file_paths: List of file paths
        
    Returns:
        List of candidate dictionaries
    """
    candidates = []
    for file_path in file_paths:
        try:
            candidate = parse_resume(file_path)
            candidates.append(candidate)
        except Exception as e:
            logger.error(f"Error processing {file_path}: {str(e)}")
            continue
    return candidates


def format_as_json(candidate_data: Dict) -> str:
    """Format candidate data as JSON string."""
    import json
    formatted_data = {
        'name': candidate_data.get('name') or '',
        'email': candidate_data.get('email') or '',
        'phone': candidate_data.get('phone') or ''
    }
    return json.dumps(formatted_data)
