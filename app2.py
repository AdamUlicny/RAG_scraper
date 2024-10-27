import streamlit as st
import pdfplumber
import re
import json
import csv
import pandas as pd
import subprocess
import tempfile
from src.answer_generation.generate_answer import generate_answer, initialize_ollama_connection
from streamlit import session_state
from streamlit_pdf_viewer import pdf_viewer
from scraper import extract_scientific_names_and_threats
from inspect import getsource

# Set up Streamlit app
st.title("PDF Data Extraction and Script Generation App")

# Step 1: Upload PDF File
uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")
# Step 2: View PDF file
if uploaded_file:
    # Save the uploaded file to a temporary location
    binary_data=uploaded_file.read()
    pdf_viewer(input=binary_data, width=700, height=800, render_text=True)

    # Reload the file for pdfplumber to extract text
    uploaded_file.seek(0)
    with pdfplumber.open(uploaded_file) as pdf:
        total_pages = len(pdf.pages)

    # Step 3: Page Selection
    page_num = st.number_input("Select Page Number to Extract Text", min_value=1, max_value=total_pages, step=1)
        
        # Extract text from the selected page
    page_text = pdf.pages[page_num - 1].extract_text()
    if page_text:
            st.text_area("Extracted Text from Selected Page", page_text, height=300)
    else:
            st.warning("No text found on this page. Try another page.")
            
        # Store the page text for later use
    st.session_state["page_text"] = page_text

output_path = st.text_input("Specify Output Path (e.g., /tmp/scraped_data.csv or /tmp/scraped_data.json)")
# Step 4: Define Prompt for Data Extraction
if uploaded_file and "page_text" in st.session_state:
    # User instruction for prompting
    script_text = getsource(extract_scientific_names_and_threats)
    context = page_text
    user_instruction = st.text_input("Describe the data to extract from the PDF page")
    question = f"""
    Update the provided Python scraping script to extract the following data from the PDF file:
    Provided Python script: {script_text}
    Data to extract: {user_instruction}

    Use the following example page to infer the structure and format of data on each page:
    {context}
    """
    # Optional llm models
    llm_models = [
    "llama3.2:latest", 
    "deepseek-coder-v2", 
    "qwen2.5:14b",
    "mistral:7b",
]
    # Choose LLM model
    llm_model = st.selectbox("Select LLM Model", llm_models)

    # Step 5: Generate Script with Ollama
    if st.button("Generate Python Script"):
        base_url = initialize_ollama_connection()  # Connect to Ollama API
        response_text = generate_answer(base_url, question, llm_model)  # Generate script using Ollama
        
        if "Error" in response_text:
            st.error(response_text)
        else:
            # Extract the code block between triple backticks
            code_block_match = re.search(r"```python(.*?)```", response_text, re.DOTALL)
            if code_block_match:
                # Get the code from within the code block
                script_text = code_block_match.group(1).strip()
                st.subheader("Generated Python Script:")
                st.code(script_text, language="python")
                
                # Store in session state for execution
                st.session_state["generated_script"] = script_text
            else:
                st.warning("No code block found in response.")

# Step 7: Execute the Generated Script with Subprocess
def run_generated_script(script_code, pdf_file_path, output_path):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as temp_script_file:
        # Write the code to a temporary script file
        temp_script_file.write(script_code.encode("utf-8"))
        temp_script_file_path = temp_script_file.name

    try:
        # Run the script as a subprocess and capture any output or errors
        result = subprocess.run(
            ["python", temp_script_file_path, pdf_file_path, output_path],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Display output and errors if any
        st.success(f"Script executed successfully. Data saved at {output_path}")
        if result.stdout:
            st.text_area("Script Output", result.stdout, height=200)
        if result.stderr:
            st.text_area("Script Errors", result.stderr, height=200)

    except subprocess.CalledProcessError as e:
        st.error("Error running script:")
        st.text(e.stderr)
    
    finally:
        # Clean up temporary script file
        temp_script_file.close()

if "generated_script" in st.session_state and output_path:
    if st.button("Run Script for Entire PDF"):
        # Save the uploaded PDF file to a temporary path
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf_file:
            temp_pdf_file.write(uploaded_file.read())
            pdf_file_path = temp_pdf_file.name
        
        # Run the generated script as a subprocess
        run_generated_script(st.session_state["generated_script"], pdf_file_path, output_path)