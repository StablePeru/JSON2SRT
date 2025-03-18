"""
Utilities for processing text in subtitle files.
"""
import re

def remove_parentheses_content(text):
    """
    Removes parentheses and their content from text.
    
    Args:
        text (str): Input text
        
    Returns:
        str: Text with parentheses content removed
    """
    if text is None:
        return ""
    return re.sub(r'\([^)]*\)', '', text).replace('  ', ' ').strip()