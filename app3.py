import streamlit as st
import json
import pdfplumber
import re
import subprocess
import tempfile
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

script_path = "/home/adam/CODE/RAG_scraper/scraper.py"

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
Update the provided Python script {original_script}
to extract the following data: {user_instruction} 
based on the provided sample page: {context}

Please return the response in valid structured JSON format as follows: 
{{
    "code":```<Updated Code Here>```
}}
- update the existing script to extract the data as described
- The code should be formatted without additional newline characters (`\n`) or escape sequences unless absolutely necessary.
- Return the code in a single JSON-compatible string without additional formatting.
"""
    
    # Optional llm models
    llm_models = [
        "llama3.2:latest",
        "deepseek-coder-v2",
        "qwen2.5:14b",
        "mistral:7b"
    ]
    
    # Choose LLM model
    selected_llm_model = st.selectbox("Select LLM Model", llm_models)
    
    # Generate the answer from the LLM API
    if st.button("Generate Python Script"):
        base_url = initialize_ollama_connection()
        response_text = generate_answer(base_url, question, selected_llm_model)
        
        # Display the raw response text for debugging purposes
        st.write("Raw Response from LLM:", response_text)  # Display in Streamlit
        print("Raw Response from LLM:", response_text)  # Print to console

        # Step 1: Check if response_text is already a dict
        if isinstance(response_text, dict):
            response_json = response_text  # Already a dictionary, no need for json.loads()
        else:
            try:
                response_json = json.loads(response_text)  # Parse if it's a string
            except json.JSONDecodeError:
                st.error("Failed to parse JSON response from the API.")
                response_json = None

        # Step 2: Process the parsed JSON
        if response_json:
            # Check if an error field is present
            if "error" in response_json:
                st.error(response_json["error"])
                print("Error in Response:", response_json["error"])  # Log error to console

            # Try to extract the code field
            elif "response" in response_json:
                response_text = response_json["response"]

        # Use regex to find code block within triple backticks labeled as python
        code_block_match = re.search(r"```(.*?)```", response_text, re.DOTALL)

        if code_block_match:
            script_text = code_block_match.group(1).strip()

            # Display and store the extracted code
            st.subheader("Generated Python Script:")
            st.code(script_text, language="python")
            st.session_state["generated_script"] = script_text  # Store for execution

        else:
            # If "code" field is not found, display the entire JSON response
            st.warning("No 'code' field found in JSON response.")
            st.write("Full JSON response for inspection:", response_json)
            print("Full JSON response:", response_json)  # Log to console for debugging

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