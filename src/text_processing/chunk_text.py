# src/text_processing/chunk_text.py

import re

def chunk_text(text, chunk_size, chunk_overlap):
    """
    Splits the text into overlapping chunks of specified size.
    
    Parameters:
    text (str): The input text to be chunked.
    chunk_size (int): The maximum size of each chunk (in characters).
    chunk_overlap (int): The number of overlapping characters between chunks.
    
    Returns:
    list of str: A list of text chunks.
    """
    chunks = []
    
    # Clean up text by removing excessive whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Start splitting the text into chunks
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        
        # Append the chunk to our list of chunks
        chunks.append(chunk.strip())
        
        # Move the start position by chunk_size minus the overlap
        start += chunk_size - chunk_overlap
    
    return chunks
