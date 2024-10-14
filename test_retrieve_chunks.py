# test_retrieve_chunks.py (temporary script for testing)

from src.pdf_processing.extract_text import extract_text_from_pdf
from src.text_processing.clean_text import clean_text
from src.text_processing.chunk_text import chunk_text
from src.embeddings.embed_text import embed_text_chunks
from src.retrieval.retrieve_chunks import initialize_chroma_collection, add_chunks_to_chroma, retrieve_similar_chunks

# Sample file and sample query
file_path = "data/uploads/sample.pdf"
query_text = "What is the main topic of the document?"

# Step 1: Extract, clean, and chunk text
raw_text = extract_text_from_pdf(file_path)
cleaned_text = clean_text(raw_text)
chunks = chunk_text(cleaned_text, chunk_size=500, chunk_overlap=50)

# Step 2: Embed chunks and query text
embeddings = embed_text_chunks(chunks)
query_embedding = embed_text_chunks([query_text])[0]

# Step 3: Initialize ChromaDB collection and add chunks
collection = initialize_chroma_collection("test_document_chunks")
add_chunks_to_chroma(chunks, collection)

# Step 4: Retrieve similar chunks based on the query
similar_chunks = retrieve_similar_chunks(query_embedding, collection, top_k=3)
print("Top relevant chunks:")
for result in similar_chunks:
    print(result["chunk"])
