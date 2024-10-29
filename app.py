import streamlit as st
import pdfplumber
from PIL import Image
import io
import tabula
from src.pdf_processing.extract_text import extract_text_from_pdf
from src.text_processing.clean_text import clean_text
from src.text_processing.chunk_text import chunk_text
from src.retrieval.retrieve_chunks import initialize_chroma_collection, add_chunks_to_chroma, retrieve_similar_chunks
from src.embeddings.embed_text import embed_text_chunks
from src.answer_generation.generate_answer import initialize_ollama_connection

# Set up Streamlit app
st.title("Enhanced RAG App for Data Extraction from PDFs")

# Step 1: Upload and Display PDF
uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")
if uploaded_file:
    pdf = pdfplumber.open(io.BytesIO(uploaded_file.read()))
    st.write("Browse PDF pages and select text or table areas to extract.")

    # Step 2: Display pages with selection option
    selected_texts = []
    for i, page in enumerate(pdf.pages):
        st.write(f"Page {i + 1}")
        image = page.to_image().convert("RGB")
        image_buffer = io.BytesIO()
        image.save(image_buffer, format="PNG")
        st.image(image_buffer.getvalue(), caption=f"Page {i + 1}")

        # Selection input (coordinates or text for scraping)
        selected_area = st.text_area(f"Select area on Page {i + 1} (e.g., 'Coordinates or Text')")
        selected_texts.append((i + 1, selected_area))

# Step 3: Chunking and Cleaning
chunk_size = st.slider("Set Chunk Size", min_value=100, max_value=1000, value=500, step=50)
chunk_overlap = st.slider("Set Chunk Overlap", min_value=0, max_value=500, value=100, step=50)

if st.button("Chunk and Clean Text"):
    if uploaded_file:
        raw_text = extract_text_from_pdf(uploaded_file)
        cleaned_text = clean_text(raw_text)
        chunks = chunk_text(cleaned_text, chunk_size, chunk_overlap)
        st.session_state["chunks"] = chunks
        st.success("Text chunked and cleaned!")
    else:
        st.error("Please upload a PDF file first.")

# Step 4: Embedding and Retrieval
if st.button("Generate Embeddings and Retrieve Context"):
    if uploaded_file:
        chunks = st.session_state["chunks"]
        collection = initialize_chroma_collection("chunk_db")
        add_chunks_to_chroma(chunks, collection)
        prompt = st.text_input("Prompt for Extraction", "What are the species and their threat levels?")
        similar_chunks = retrieve_similar_chunks(prompt, collection, top_k=3)
        context = " ".join([result["chunk"] for result in similar_chunks])
        st.session_state["context"] = context
        st.success("Context retrieved from embeddings!")
    else:
        st.error("Please upload a PDF file first.")

## Step 5: LLM Prompting and Script Generation
llm_model = st.selectbox("Select LLM Model", ["llama3.2:latest", "llama3.2:3b-instruct-q2_K", "qwen2.5:latest"])
if st.button("Generate Extraction Script"):
    if uploaded_file:
        context = st.session_state["context"]
        ollama_base_url = initialize_ollama_connection()
        selected_info = " ".join([f"Page {p}: {txt}" for p, txt in selected_texts if txt])
        
        # Send selected info and prompt to LLM
        full_prompt = f"Generate a Python script to extract data based on selected areas:\n{selected_info}\nContext:\n{context}"
        answer = generate_answer(ollama_base_url, full_prompt, context)
        
        # Display generated script
        st.write("Generated Python Script:")
        st.code(answer, language="python")
        st.session_state["generated_script"] = answer
    else:
        st.error("Please upload a PDF file first.")

# Step 6: Run Generated Script and Display Results
if st.button("Run Generated Script"):
    if "generated_script" in st.session_state:
        exec(st.session_state["generated_script"])  # Caution: Ensure safety when running code
        st.write("Script executed. Check output for extracted data.")
    else:
        st.error("Please generate a script first.")

# Optional: Download Script
if "generated_script" in st.session_state:
    st.download_button("Download Script", st.session_state["generated_script"], file_name="extraction_script.py")

# Optional: Use Tabula-Py for Table Extraction
if st.button("Extract Table using Tabula-Py"):
    if uploaded_file:
        # Save the uploaded PDF temporarily
        pdf_path = "/tmp/uploaded_pdf.pdf"
        with open(pdf_path, "wb") as f:
            f.write(uploaded_file.getvalue())

        # Get user-specified page and area
        page_num = st.number_input("Page number for table extraction", min_value=1, max_value=len(pdf.pages), value=1)
        coords = st.text_input("Table area coordinates (e.g., top,left,bottom,right)")

        if coords:
            # Parse coordinates and extract table
            coords = [float(c) for c in coords.split(",")]
            table = tabula.read_pdf(pdf_path, pages=page_num, area=coords, stream=True)
            st.write("Extracted Table:")
            st.dataframe(table[0] if table else "No table found.")
    else:
        st.error("Please upload a PDF file first.")