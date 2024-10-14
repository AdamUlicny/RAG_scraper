# src/text_processing/clean_text.py

import re

def clean_text(text):
    """
    Cleans extracted text by removing unnecessary whitespace, special characters, and formatting artifacts.
    
    Parameters:
    text (str): Raw extracted text from PDF.
    
    Returns:
    str: Cleaned text.
    """
    # Remove excessive whitespace and line breaks
    text = re.sub(r'\s+', ' ', text)

    # Optionally, remove or normalize special characters (e.g., hyphens at line breaks)
    text = re.sub(r'(?<!\w)-\s+', '', text)  # Removes hyphens at the end of lines

    # Strip leading and trailing whitespace
    text = text.strip()
    
    return text
