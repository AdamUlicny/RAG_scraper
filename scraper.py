import fitz  # PyMuPDF
import csv
uploaded_file = "/home/adam/Downloads/BGD_Animalia_Mammals_2015.pdf"
output_path = "/home/adam/Downloads/extracted_data.csv"

def extract_scientific_names_and_threats(uploaded_file, output_path):
    document = fitz.open(uploaded_file)
    
    # Prepare data to write to CSV
    with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Scientific Name", "Threat Category"])  # Write header
        
        for page_num in range(len(document)):
            page = document.load_page(page_num)
            
            # Extract text from the page
            text = page.get_text("text")
            
            lines = text.split("\n")
            
            scientific_name = None
            threat_category = None
            
            for line in lines:
                if "Scientific Name:" in line:
                    name_part = line.replace("Scientific Name:", "").strip()
                    
                    # Ensure that only the first two parts are captured, which should be the species name
                    parts = name_part.split(' ')
                    scientific_name = ' '.join(parts[:2])  # Take exactly the first two words
                    
                elif "<" in line and ">" in line:
                    threat_category = line.strip("<>").strip()
                    
            if scientific_name is not None and threat_category is not None:
                writer.writerow([scientific_name, threat_category])

# Example usage
extract_scientific_names_and_threats(uploaded_file, output_path)