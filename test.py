# test_retrieve_chunks.py

from src.pdf_processing.extract_text import extract_text_from_pdf
from src.text_processing.clean_text import clean_text
from src.text_processing.chunk_text import chunk_text
from src.retrieval.retrieve_chunks import initialize_chroma_collection, add_chunks_to_chroma, retrieve_similar_chunks

# Sample file and sample query
file_path = "data/uploads/sample.pdf"
query_text = "What is the main topic of the document?"

# Step 1: Extract raw text from PDF
raw_text = extract_text_from_pdf(file_path)

# Step 2: Clean the extracted text
cleaned_text = clean_text(raw_text)

# Step 3: Chunk the cleaned text
chunks = chunk_text(cleaned_text, chunk_size=500, chunk_overlap=50)

# Step 4: Initialize ChromaDB collection
collection = initialize_chroma_collection("test_document_chunks")

# Step 5: Add chunks to the ChromaDB collection
add_chunks_to_chroma(chunks, collection)

# Step 6: Retrieve similar chunks based on the query
similar_chunks = retrieve_similar_chunks(query_text, collection, top_k=3)

# Print the top relevant chunks
print("Top relevant chunks:")
for result in similar_chunks:
    print(result["chunk"])
