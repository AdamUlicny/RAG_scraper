import streamlit as st
from src.pdf_processing.pdf_ingestion import ingest_pdf  # Import your PDF ingestion function
from src.embeddings.embed_text import embed_text_chunks  # Import your embedding function
from src.answer_generation.generate_answer import generate_answer  # Import your answer generation function

# Set up Streamlit app
st.title("RAG App for Species Extraction from PDFs")

# Upload PDF file
uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")
if uploaded_file is not None:
    text = ingest_pdf(uploaded_file)  # Function to extract text from the PDF
    st.text_area("Extracted Text", text, height=300)

# Choose embedding model
embedding_model = st.selectbox("Select Embedding Model", ["nomic-embed-text", "other_model_1", "other_model_2"])

# Generate embeddings
if st.button("Generate Embeddings"):
    if uploaded_file is not None:
        chunks = text.split("\n")  # Split text into chunks; you can improve this logic
        embeddings = embed_text_chunks(chunks)  # Embed the chunks
        st.success("Embeddings generated successfully!")
    else:
        st.error("Please upload a PDF file first.")

# Choose LLM model
llm_model = st.selectbox("Select LLM Model", ["model1", "model2", "model3"])

# Change prompt
prompt = st.text_input("Change Prompt", "What are the species mentioned in the text?")

# Generate answer
if st.button("Generate Answer"):
    if uploaded_file is not None:
        answer = generate_answer("http://localhost:11434", prompt, text)  # Adjust URL as needed
        st.write("Generated Answer:")
        st.success(answer)
    else:
        st.error("Please upload a PDF file first.")

# Delete embeddings
if st.button("Delete Embeddings"):
    # Implement the logic to delete embeddings here
    st.success("Embeddings deleted successfully!")

# Additional functionality could be added as needed
