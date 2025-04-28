import requests
import streamlit as st
import json
import pdfplumber
import re
import subprocess
import tempfile
import logging
from src.answer_generation.generate_answer import generate_answer, initialize_ollama_connection
from streamlit_pdf_viewer import pdf_viewer

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

script_path = "scraper.py"

# Read the entire file into a string
with open(script_path, "r") as file:
    original_script = file.read()

output_path = st.text_input("Specify Output Path (e.g., /tmp/scraped_data.csv or /tmp/scraped_data.json)")

# Step 4: Define Prompt for Data Extraction
if uploaded_file and "page_text" in st.session_state:
    # User instruction for prompting
    context = st.session_state["page_text"]
    
    user_instruction = st.text_input("Describe the data to extract from the PDF page")
    question = f"""
Your task is to update a scraping script to extract specified data from a PDF document.
Script to update: {original_script}

Data to extract: {user_instruction} 

Sample page to understand text structure: {context}

Instead of \n for new lines, use the actual newline character. This is very important.
Make sure the updated code will be able to run as a standalone script.
In the codeblock, ensure correct indentation and formatting.
"""
    
    # Optional llm models
    llm_models = [
        "llama3.1",
        "llama3.2:latest",
        "deepseek-coder-v2",
        "qwen2.5:14b",
        "mistral:7b",
        "codellama:latest",
        "qwen2.5:1.5b",
        "qwen2.5:1.5b-instruct",
        "llama3.2:3b",
        "llama3.2:3b-instruct-fp16"
    ]
    
    # Choose LLM model
    selected_llm_model = st.selectbox("Select LLM Model", llm_models)
    
    # Generate the answer from the LLM API
    if st.button("Generate Python Script"):
        base_url = initialize_ollama_connection()
        response_text = generate_answer(base_url, question, selected_llm_model)

        # Display the raw response text for debugging purposes
        st.write("Raw Response from LLM:", response_text)  # Display in Streamlit
        print("Raw Response from LLM:", response_text) # Display in console
        # Step 1: Check if response_text contains the updated code
        try:
            # Extract the code part from the response text using a specific symbol
            code_start = response_text.find("###START_CODE###") + len("###START_CODE###")
            code_end = response_text.find("###END_CODE###", code_start)
            if code_start != -1 and code_end != -1:
                generated_code = response_text[code_start:code_end].strip()
                st.session_state["generated_script"] = generated_code
            else:
                st.error("Error: Code markers not found in the response text.")
        
        except requests.exceptions.RequestException as e:
            logging.error(f"Error connecting to Ollama API: {e}")
            st.error("Error connecting to Ollama API.")
        
        except json.JSONDecodeError:
            logging.error("Failed to decode JSON:", response_text)
            st.error("Error: Unexpected response format from Ollama API.")

# Execute the Generated Script with Subprocess
def run_generated_script(script_code, pdf_file_path, output_path):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as temp_script_file:
        temp_script_file.write(script_code.encode("utf-8"))
        temp_script_file_path = temp_script_file.name

    try:
        result = subprocess.run(
            ["python", temp_script_file_path, pdf_file_path, output_path],
            capture_output=True,
            text=True,
            check=True
        )
        
        st.success(f"Script executed successfully. Data saved at {output_path}")
        if result.stdout:
            st.text_area("Script Output", result.stdout, height=200)
        if result.stderr:
            st.text_area("Script Errors", result.stderr, height=200)

    except subprocess.CalledProcessError as e:
        st.error("Error running script:")
        st.text(e.stderr)
    
    finally:
        temp_script_file.close()

if "generated_script" in st.session_state and output_path:
    if st.button("Run Script for Entire PDF"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf_file:
            temp_pdf_file.write(uploaded_file.read())
            pdf_file_path = temp_pdf_file.name
        
        run_generated_script(st.session_state["generated_script"], pdf_file_path, output_path)