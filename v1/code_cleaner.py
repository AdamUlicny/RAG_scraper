import re

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
# Example usage
script = r'''\nimport fitz  # PyMuPDF\nimport csv  # Necessary for writing CSV file\n\n# Path provided in /tmp/tmp46vo6jz2/BGD_Animalia_Mammals_2015.pdf for input path\ninput_path = \"/tmp/tmp46vo6jz2/BGD_Animalia_Mammals_2015.pdf\"\noutput_path = \"/home/adam/data.csv\"  # Path provided in /home/adam/data.csv for output path\n\ndef extract_scientific_names_and_threats(input_file, output_file):\n    \"\"\"\n    Extract scientific names and threat categories from a PDF file and write them to a CSV file.\n    \n    Parameters:\n    input_file (str): The path to the PDF file.\n    output_file (str): The path to the CSV file where results will be written.\n    \"\"\"\n\n    # Open the PDF file\n    document = fitz.open(input_file)\n    \n    # Prepare data to write to CSV\n    with open(output_file, \"w\", newline=\"\", encoding=\"utf-8\") as csvfile:\n        writer = csv.writer(csvfile)\n        writer.writerow([\"Scientific Name\", \"Threat Category\", \"Regional Status\"])  # Write header\n        \n        for page_num in range(len(document)):\n            page = document.load_page(page_num)\n            \n            text = page.get_text(\"text\")\n            \n            lines = text.split(\"\\n\")\n            \n            scientific_name = None\n            threat_category = None\n            \n            for line in lines:\n                if \"Scientific Name:\" in line:\n                    name_part = line.replace(\"Scientific Name:\", \"\").strip()\n                    \n                    parts = name_part.split(' ')\n                    scientific_name = ' '.join(parts[:2])  # Take exactly the first two words\n                    \n                elif \"\u003c\" in line and \"\u003e\" in line:\n                    threat_category = line.strip(\"\u003c\u003e\").strip()\n                    \n            if scientific_name is not None and threat_category is not None:\n                writer.writerow([scientific_name, threat_category, \"Not Threatened in Bangladesh\"])\n\n# Example usage\nextract_scientific_names_and_threats(input_path, output_path)\n'''

cleaned_script = clean_script_code(script)
print(cleaned_script)