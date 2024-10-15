import streamlit as st
from src.pdf_processing.extract_text import extract_text_from_pdf  # Import your PDF ingestion function
from src.text_processing.clean_text import clean_text # import text cleaning
from src.text_processing.chunk_text import chunk_text # import text chunking
from src.retrieval.retrieve_chunks import initialize_chroma_collection, add_chunks_to_chroma, retrieve_similar_chunks # import chromadb
from src.embeddings.embed_text import embed_text_chunks  # Import your embedding function
from src.answer_generation.generate_answer import generate_answer, initialize_ollama_connection  # Import your answer generation function

# Set up Streamlit app
st.title("RAG App for TESTING Data Extraction from PDFs")

# Upload PDF file
uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")
if uploaded_file is not None:
    raw_text = extract_text_from_pdf(uploaded_file)  # Function to extract text from the PDF
    st.text_area("Extracted Text", raw_text, height=300)


# Chunk size and overlap settings
chunk_size = st.slider("Set Chunk Size", min_value=100, max_value=1000, value=500, step=50)
chunk_overlap = st.slider("Set Chunk Overlap", min_value=0, max_value=500, value=100, step=50)

# Chunk the text
if st.button("Chunk Text"):
    if uploaded_file is not None:
        cleaned_text = clean_text(raw_text)
        chunks = chunk_text(cleaned_text, chunk_size, chunk_overlap)
        st.session_state["chunks"] = chunks  # Store chunks in session state
        st.success("Chunked and cleaned text successfully!")
    else:
        st.error("Please upload a PDF file first.")



# Change prompt
prompt = st.text_input("Change Prompt", "What are the species mentioned in the text?")


embedding_models = [
    "nomic-embed-text", 
    "mxbai-embed-large", 
    "snowflake-arctic-embed"
]

llm_models = [
    "llama3.2:latest", 
    "llama3.2:3b-instruct-q2_K", 
    "qwen2.5:latest",
    "gemma2:2b",
    "qwen2.5:1.5b-instruct",
]


# Choose embedding model
#embedding_model = st.selectbox("Select Embedding Model", embedding_models)

# Generate embeddings
if st.button("Generate Embeddings"):
    if uploaded_file is not None:
        chunks = st.session_state["chunks"]
        collection = initialize_chroma_collection(collection_name="chunk_db")
        add_chunks_to_chroma(chunks, collection)
        similar_chunks = retrieve_similar_chunks(prompt, collection, top_k=3)
        context = " ".join([result["chunk"] for result in similar_chunks])
        st.session_state["context"] = context
        st.success("Embeddings generated successfully!")
    else:
        st.error("Please upload a PDF file first.")

# Choose LLM model
llm_model = st.selectbox("Select LLM Model", llm_models)



# Generate answer
if st.button("Generate Answer"):
    if uploaded_file is not None:
        context = st.session_state["context"]
        ollama_base_url = initialize_ollama_connection()
        answer = generate_answer(ollama_base_url, prompt, context)
        st.write("Generated Answer:")
        st.success(answer)
    else:
        st.error("Please upload a PDF file first.")

# Delete embeddings
if st.button("Delete Embeddings"):
    # Implement the logic to delete embeddings here
    st.success("Embeddings deleted successfully!")

# Additional functionality could be added as needed
