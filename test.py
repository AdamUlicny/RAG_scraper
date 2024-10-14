# test_chunk_text.py (temporary script for testing)

from src.text_processing.chunk_text import chunk_text
from src.pdf_processing.extract_text import extract_text_from_pdf

# Extract text from a PDF file (from previous step)
file_path = "data/uploads/sample.pdf"
pdf_text = extract_text_from_pdf(file_path)

# Chunk the extracted text
chunks = chunk_text(pdf_text, chunk_size=500, chunk_overlap=50)
print(f"Number of chunks: {len(chunks)}")
print("First chunk:\n", chunks[0])
