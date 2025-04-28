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

#PC script_path = "/home/ulicny/GITHUB/RAG_scraper/scraper.py"
#ntb
script_path = "scraper.py"

# Read the entire file into a string
with open(script_path, "r") as file:
    original_script = file.read()
input_path = "/home/ulicny/data.pdf"
output_path = st.text_input("Specify Output Path (e.g., /tmp/scraped_data.csv or /tmp/scraped_data.json)")

#Define Prompt for Data Extraction
if uploaded_file and "page_text" in st.session_state:
    # User instruction for prompting
    context = st.session_state["page_text"]
    
    user_instruction = st.text_input("Describe the data to extract from the PDF page")
    question = f"""
You are tasked with writing a simple python script to extract specified data from a PDF.
Sample page to understand the text structure: {context}
The goal is to extract this data: {user_instruction}
Use this strin {input_path} as output path.
Use this string {output_path} as output path.
Important:
- provide well formatted codeblock, no instructions, no explainers, no comments.
- format the code as a single markdown formatted codeblock.
    """
    
    # Optional LLM models
    llm_models = [
        "llama3.1",
        "deepseek-coder-v2",
        "qwen2.5:14b",
        "qwen2.5-coder:14b",
        "qwen2.5:14b-",
    ]
    
    # Choose LLM model
    llm_model = st.selectbox("Select LLM Model", llm_models)
    
    if st.button("Generate Python Script"):
        base_url = initialize_ollama_connection()  # Connect to Ollama API
        response_text = generate_answer(base_url, question, llm_model)
        
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
    lines = script_code.split("\n")
    cleaned_lines = []
    current_line = ""
    string_state = "outside_string"
    quote_char = None

    for line in lines:
        if string_state == "outside_string":
            if "lines = text.split(\"\\n\")" in line:
                cleaned_lines.append(line)
                continue
            stripped_line = line.strip()
            if stripped_line.startswith("'''") or stripped_line.startswith('"""'):
                if stripped_line.endswith("'''") or stripped_line.endswith('"""'):
                    # Single-line triple-quoted string
                    cleaned_lines.append(line)
                else:
                    # Multi-line triple-quoted string
                    current_line = line
                    quote_char = stripped_line[:3]
                    string_state = "inside_triple_quote"
            elif stripped_line.startswith("'") or stripped_line.startswith('"'):
                if stripped_line.endswith("'") or stripped_line.endswith('"'):
                    # Single-line string
                    cleaned_lines.append(line)
                else:
                    # Multi-line string
                    current_line = line
                    quote_char = stripped_line[0]
                    string_state = "inside_single_quote" if quote_char == "'" else "inside_double_quote"
            else:
                # Non-string line
                line = line.replace("\\n", "\n").replace("\\t", "\t")
                cleaned_lines.append(line)
        else:
            current_line += "\n" + line
            if string_state == "inside_single_quote":
                if "'" in line and line[line.index("'")-1] != "\\":
                    string_state = "outside_string"
                    cleaned_lines.append(current_line)
                    current_line = ""
            elif string_state == "inside_double_quote":
                if '"' in line and line[line.index('"')-1] != "\\":
                    string_state = "outside_string"
                    cleaned_lines.append(current_line)
                    current_line = ""
            elif string_state == "inside_triple_quote":
                if stripped_line.endswith("'''") or stripped_line.endswith('"""'):
                    string_state = "outside_string"
                    cleaned_lines.append(current_line)
                    current_line = ""

    return "\n".join(cleaned_lines)

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