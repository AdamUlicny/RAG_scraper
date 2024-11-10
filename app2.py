import streamlit as st
import pdfplumber
import re
import os
import subprocess
import tempfile
import tempfile
from src.answer_generation.generate_answer import generate_answer, initialize_ollama_connection
from streamlit import session_state
from streamlit_pdf_viewer import pdf_viewer

# Set up Streamlit app
st.title("PDF Data Extraction and Script Generation App")

# Step 1: Upload PDF File
uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")
if uploaded_file:
        temp_dir = tempfile.mkdtemp()
        temp_pdf_path = os.path.join(temp_dir, uploaded_file.name)
        with open(temp_pdf_path, "wb") as f:
                f.write(uploaded_file.getvalue())

# View PDF file
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

#PC script_path = "/home/adam/CODE/RAG_scraper/scraper.py"
#ntb
script_path = "scraper.py"

# Read the entire file into a string
with open(script_path, "r") as file:
    original_script = file.read()

output_path = st.text_input("Specify Output Path (e.g., /tmp/scraped_data.csv or /tmp/scraped_data.json)")

#Define Prompt for Data Extraction
if uploaded_file and "page_text" in st.session_state:
    # User instruction for prompting
    context = st.session_state["page_text"]
    
    user_instruction = st.text_input("Describe the data to extract from the PDF page")
    question = f"""
You are tasked with updating a provided Python script to extract specified data from a PDF.
This is the script to update: {original_script}

The goal is to extract this data: {user_instruction}

Sample page to understand the text structure: {context}

Use this string {output_path} as output path.
Important:
- provide well formatted codeblock, no instructions, no explainers, no comments.
- format the code as a single markdown formatted codeblock.
    """
    
    # Optional LLM models
    llm_models = [
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
    
    if st.button("Generate Python Script"):
        base_url = initialize_ollama_connection()  # Connect to Ollama API
        response_text = generate_answer(base_url, question, selected_llm_model)
        
        if "Error" in response_text:
            st.error(response_text)
        else:
            # Extract the code block between triple backticks
            code_block_match = re.search(r"```python(.*?)```", response_text, re.DOTALL)
            if code_block_match:
                # Get the code from within the code block
                script_code = code_block_match.group(1).strip()
                st.subheader("Generated Python Script:")
                st.code(script_code, language="python")
                
                # Store in session state for execution
                st.session_state["generated_script"] = script_code
            else:
                st.warning("No code block found in response.")


def clean_script_code(script_code):
    """
    Cleans the generated script code by:
    - Preserving specific lines with newline characters in the input string
    - Converting escaped quotes (\") back to normal quotes selectively
    - Converting escaped newline (\n) and tab (\t) characters to actual newlines and tabs
    - Converting escaped unicode characters (e.g., \u003c) to their corresponding symbols
    - Handling multi-line strings and ensuring balanced quotes
    
    Args:
        script_code (str): The input script code to clean
        
    Returns:
        str: The cleaned script code
    """
    if not script_code:
        return ""
    
    # Step 1: Preserve specific lines with newline characters
    lines = script_code.split("\n")
    cleaned_lines = []
    for line in lines:
        if "lines = text.split(\"\\n\")" in line:
            cleaned_lines.append(line)
        else:
            # Convert other lines
            line = line.replace("\\n", "\n")
            line = re.sub(r'\\"', '"', line)
            line = line.replace("\\t", "\t")
            try:
                line = bytes(line, "utf-8").decode("unicode_escape")
            except UnicodeDecodeError:
                pass
            cleaned_lines.append(line)
    
    # Step 2: Handle balanced quotes and multi-line strings for the remaining lines
    balanced_lines = []
    open_quote = None
    current_line = ""
    
    for line in cleaned_lines:
        if not line:
            balanced_lines.append("")
            continue
            
        if open_quote:
            # We're inside a multi-line string
            current_line += "\n" + line
            
            # Check if this line contains the closing quote
            quote_positions = [i for i, char in enumerate(line) if char == open_quote]
            for pos in quote_positions:
                # Make sure it's not escaped
                if pos > 0 and line[pos-1] != "\\":
                    balanced_lines.append(current_line)
                    current_line = line[pos+1:]
                    open_quote = None
                    break
                    
            if open_quote:  # Still open
                continue
                
        else:
            current_line = line
            
        # Look for new quote openings
        for char in ['"', "'"]:
            quote_positions = [i for i, c in enumerate(current_line) if c == char]
            quote_count = len(quote_positions)
            
            if quote_count % 2 == 1:  # Odd number of quotes
                # Find the position of the last quote
                last_quote_pos = quote_positions[-1]
                # Check if it's not escaped
                if last_quote_pos == 0 or current_line[last_quote_pos-1] != "\\":
                    open_quote = char
                    break
        
        if not open_quote:
            balanced_lines.append(current_line)
        else:
            current_line = line
            
    # Handle any remaining open quotes
    if current_line:
        balanced_lines.append(current_line)
    
    return "\n".join(balanced_lines)

# Execute the Generated Script with Subprocess
def run_generated_script(script_code, pdf_file_path, output_path):
    cleaned_script_code = clean_script_code(script_code)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as temp_script_file:
        temp_script_file.write(cleaned_script_code.encode("utf-8"))
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
    

if "generated_script" in st.session_state and output_path:
    if st.button("Run Script for Entire PDF"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf_file:
            temp_pdf_file.write(uploaded_file.read())
            pdf_file_path = temp_pdf_file.name
        
        run_generated_script(st.session_state["generated_script"], pdf_file_path, output_path)