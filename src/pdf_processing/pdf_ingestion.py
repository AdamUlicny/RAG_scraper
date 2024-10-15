# src/pdf_processing/pdf_ingestion.py

import fitz  # PyMuPDF

def ingest_pdf(uploaded_file):
    """
    Extract text from a PDF file.

    Parameters:
    uploaded_file (file-like object): The uploaded PDF file.

    Returns:
    str: Extracted text from the PDF.
    """
    # Open the PDF file
    pdf_document = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    
    text = ""
    for page in pdf_document:
        text += page.get_text()  # Extract text from each page

    pdf_document.close()
    return text
