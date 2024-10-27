import streamlit as st
import pdfplumber
import re
import json
import pandas as pd
from src.answer_generation.generate_answer import generate_answer, initialize_ollama_connection
from streamlit import session_state
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

# Step 4: Define Prompt for Data Extraction
if uploaded_file and "page_text" in st.session_state:
    # User instruction for prompting
    context = page_text
    user_instruction = st.text_input("Describe the data to extract (e.g., 'Extract table of species and their threat levels')")
    question = f"""
    Generate a Python script that iterates through each page of a PDF to extract the following data, and saves all results in {output_format} format at the specified path:
    
    Data to extract: {user_instruction}
    Example page from PDF: {context}

    The PDF file is provided as a variable `uploaded_file`.
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

    output_format = st.selectbox("Select Output Format", ["CSV", "JSON"])
    output_path = st.text_input("Specify Output Path (e.g., /tmp/scraped_data.csv or /tmp/scraped_data.json)")

    # Step 5: Generate Script with Ollama
    if st.button("Generate Python Script"):
        base_url = initialize_ollama_connection()  # Connect to Ollama API
        response_text = generate_answer(base_url, question, context, llm_model)  # Generate script using Ollama
        
        if "Error" in response_text:
            st.error(response_text)
        else:
            # Extract the code block between triple backticks
            code_block_match = re.search(r"```(.*?)```", response_text, re.DOTALL)
            if code_block_match:
                # Get the code from within the code block
                script_text = code_block_match.group(1).strip()
                st.subheader("Generated Python Script:")
                st.code(script_text, language="python")
                
                # Store in session state for execution
                st.session_state["generated_script"] = script_text
            else:
                st.warning("No code block found in response.")

# Step 5: Execute the Generated Script with Output Specifications
def run_generated_script(script_code, pdf_file, output_path):
    # Prepare local namespace with pdf file and output path for exec()
    local_vars = {"uploaded_file": pdf_file, "output_path": output_path}
    
    # Execute the script in the local scope with defined variables
    exec(script_code, {}, local_vars)

if "generated_script" in st.session_state and output_path:
    if st.button("Run Script for Entire PDF"):
        run_generated_script(st.session_state["generated_script"], uploaded_file, output_path)
        st.success(f"Script executed and data saved at {output_path}")

        # Display results based on output format
        if output_format == "CSV":
            result_data = pd.read_csv(output_path)
            st.dataframe(result_data)
        elif output_format == "JSON":
            with open(output_path, "r") as f:
                result_data = json.load(f)
            st.json(result_data)