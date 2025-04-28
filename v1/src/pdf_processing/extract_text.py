# src/pdf_processing/extract_text.py

import pdfplumber
import fitz  # PyMuPDF

def extract_text_from_pdf(file_path):
    """
    Extracts text from a text-based PDF using pdfplumber and PyMuPDF as a fallback.
    
    Parameters:
    file_path (str): Path to the PDF file.
    
    Returns:
    str: Extracted text from the PDF.
    """
    text = ""

    # Primary method: Attempt to extract text using pdfplumber
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print("pdfplumber failed. Error:", e)
        text = ""  # Reset text if pdfplumber fails

    # Fallback method: If pdfplumber fails, use PyMuPDF (fitz)
    if not text.strip():
        try:
            pdf_document = fitz.open(file_path)
            for page_num in range(pdf_document.page_count):
                page = pdf_document[page_num]
                text += page.get_text() + "\n"
        except Exception as e:
            print("PyMuPDF also failed. Error:", e)
    
    return text.strip()
