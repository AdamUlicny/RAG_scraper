import requests
from bs4 import BeautifulSoup
import csv
import os
import re
from transliterate import translit
from googletrans import Translator

def clean_filename(text):
    """Clean text to create valid filename with transliteration"""
    try:
        # Transliterate Russian to Latin characters
        latinized = translit(text, 'ru', reversed=True)
    except:
        # If transliteration fails, use original text
        latinized = text
    
    # Replace spaces and other unwanted characters with underscores
    cleaned = re.sub(r'[^\w\s-]', '', latinized)
    cleaned = re.sub(r'\s+', '_', cleaned.strip())
    return cleaned

def translate_text(text):
    """Translate Russian text to English"""
    try:
        translator = Translator()
        translation = translator.translate(text, src='ru', dest='en')
        return translation.text
    except Exception as e:
        print(f"Translation error for '{text}': {str(e)}")
        return text

def download_pdf(url, filename):
    """Download PDF file"""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        if not os.path.exists('pdfs'):
            os.makedirs('pdfs')
            
        filepath = os.path.join('pdfs', filename)
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        return True
    except Exception as e:
        print(f"Error downloading {url}: {str(e)}")
        return False

def scrape_entry_page(base_url, entry_url):
    """Scrape individual entry page for PDF URL"""
    try:
        response = requests.get(base_url + entry_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        doc_row = soup.find('td', text='Document:')
        if doc_row and doc_row.find_next_sibling('td'):
            pdf_link = doc_row.find_next_sibling('td').find('a')
            if pdf_link:
                return pdf_link['href']
    except Exception as e:
        print(f"Error scraping entry page {entry_url}: {str(e)}")
    return None

def main():
    base_url = 'https://www.plantarium.ru'
    main_url = base_url + '/lang/en/page/redbooks.html'
    
    with open('redbooks_data.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['region_russian', 'region_transliterated', 'region_english', 
                     'year', 'source_name', 'pdf_name', 'pdf_url']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        try:
            response = requests.get(main_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            rows = soup.find_all('tr', class_='row-lined')
            
            for row in rows:
                region_cell = row.find('td').find_next_sibling('td')
                if not region_cell:
                    continue
                    
                region_russian = region_cell.text.strip()
                region_transliterated = clean_filename(region_russian)
                region_english = translate_text(region_russian)
                
                year = region_cell.find_next_sibling('td').text.strip()
                source_name = region_cell.find_next_sibling('td').find_next_sibling('td').find_next_sibling('td').text.strip()
                
                pdf_name = f"{region_transliterated}_{year}.pdf"
                
                print(f"Processing: {region_russian} -> {region_transliterated} -> {region_english}")
                
                entry_link = region_cell.find('a')
                if entry_link:
                    pdf_url = scrape_entry_page(base_url, entry_link['href'])
                    if pdf_url:
                        if download_pdf(pdf_url, pdf_name):
                            print(f"Successfully downloaded: {pdf_name}")
                    
                    writer.writerow({
                        'region_russian': region_russian,
                        'region_transliterated': region_transliterated,
                        'region_english': region_english,
                        'year': year,
                        'source_name': source_name,
                        'pdf_name': pdf_name,
                        'pdf_url': pdf_url if pdf_url else ''
                    })
                    
        except Exception as e:
            print(f"Error scraping main page: {str(e)}")

if __name__ == "__main__":
    main()