# test_retrieve_chunks.py

from src.pdf_processing.extract_text import extract_text_from_pdf
from src.text_processing.clean_text import clean_text
from src.text_processing.chunk_text import chunk_text
from src.retrieval.retrieve_chunks import initialize_chroma_collection, add_chunks_to_chroma, retrieve_similar_chunks
from src.answer_generation.generate_answer import initialize_ollama_connection, generate_answer

# Sample file and query
file_path = "data/uploads/sample.pdf"
query_text = "List all"

# Step 1: Extract, clean, and chunk text
raw_text = extract_text_from_pdf(file_path)
cleaned_text = clean_text(raw_text)
chunks = chunk_text(cleaned_text, chunk_size=500, chunk_overlap=50)
    
# Step 2: Initialize ChromaDB collection and add chunks
collection = initialize_chroma_collection("test_document_chunks")
add_chunks_to_chroma(chunks, collection)

# Step 3: Retrieve relevant chunks
similar_chunks = retrieve_similar_chunks(query_text, collection, top_k=3)
context = " ".join([result["chunk"] for result in similar_chunks])

# Step 4: Generate answer with Ollama
ollama_base_url = initialize_ollama_connection()
answer = generate_answer(ollama_base_url, query_text, context)
print("Answer:", answer)
