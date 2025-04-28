import fitz 
import csv 
uploaded_file = 
output_path = 

def extract_scientific_names_and_threats(uploaded_file, output_path):
    document = fitz.open(uploaded_file)

    with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Scientific Name", "Threat Category"]) 
        
        for page_num in range(len(document)):
            page = document.load_page(page_num)
            
            text = page.get_text("text")
            
            lines = text.split("\n")
            
            scientific_name = None
            threat_category = None
            
            for line in lines:
                if "Scientific Name:" in line:
                    name_part = line.replace("Scientific Name:", "").strip()
                
                    parts = name_part.split(' ')
                    scientific_name = ' '.join(parts[:2])
                    
                elif "<" in line and ">" in line:
                    threat_category = line.strip("<>").strip()
                    
            if scientific_name is not None and threat_category is not None:
                writer.writerow([scientific_name, threat_category])

extract_scientific_names_and_threats(uploaded_file, output_path)