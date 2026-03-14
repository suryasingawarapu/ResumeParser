"""Email-based deduplication module for the Resume Processing System."""

import logging
from typing import Dict, List, Set

# Configure logging
logger = logging.getLogger(__name__)


def deduplicate_candidates(candidates: List[Dict]) -> List[Dict]:
    """
    Remove duplicate candidates based on email address.
    
    Uses email as the unique identifier with case-insensitive comparison.
    Retains the first occurrence of each email and excludes subsequent duplicates.
    
    Args:
        candidates: List of candidate dictionaries with 'name', 'email', 'phone' fields
        
    Returns:
        List of deduplicated candidate dictionaries with first occurrence retained
        
    Requirements: 6.1, 6.2, 6.3
    """
    seen_emails: Set[str] = set()
    deduplicated = []
    
    for candidate in candidates:
        email = candidate.get('email', '').strip()
        
        # Skip candidates without email (handled by filter_missing_email)
        if not email:
            continue
        
        # Normalize email to lowercase for case-insensitive comparison
        email_lower = email.lower()
        
        # Check if we've seen this email before
        if email_lower not in seen_emails:
            seen_emails.add(email_lower)
            deduplicated.append(candidate)
        else:
            logger.debug(f"Duplicate email detected and excluded: {email}")
    
    return deduplicated


def filter_missing_email(candidates: List[Dict]) -> List[Dict]:
    """
    Filter out candidates without email addresses.
    
    Excludes candidates with empty or missing email fields from the result set.
    
    Args:
        candidates: List of candidate dictionaries with 'name', 'email', 'phone' fields
        
    Returns:
        List of candidates that have non-empty email addresses
        
    Requirements: 6.4
    """
    filtered = []
    
    for candidate in candidates:
        email = candidate.get('email', '').strip()
        
        # Include only candidates with non-empty email
        if email:
            filtered.append(candidate)
        else:
            logger.debug(f"Candidate without email excluded: {candidate.get('name', 'Unknown')}")
    
    return filtered
