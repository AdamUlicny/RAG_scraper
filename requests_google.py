from google import genai
from google.genai import types
import json
from pathlib import Path
import csv
from typing import TypedDict
import time


# Load API key from file
try:
    with open("api_key.txt", "r") as f:
        api_key = f.read().strip()  # Read and remove whitespace
except FileNotFoundError:
    print("Error: api_key.txt not found")
    exit()

# Initialize the Gemini client
client = genai.Client(api_key=api_key)

# define the schema for the expected JSON response
class SpeciesThreat(TypedDict):
    species: str
    threat_level: str

# Path to your local PDF (no httpx needed here)
file_path = Path('RL_test_1.pdf')

# Upload the PDF using the File API
sample_file = client.files.upload(
    file=file_path,
)
time.sleep(1)
# Now send prompt + file reference
prompt = "List all mentioned species scientific names and their respective (two letter) threat level categories. Format the output as a JSON array of objects, each with 'species' and 'threat_level' fields."

response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=[
        sample_file,  # This refers to the uploaded file
        prompt,
    ],
    config={
        'response_mime_type': 'application/json',
        'response_schema': list[SpeciesThreat],
    },
)

# Parse the JSON response
species_data = json.loads(response.text)

# Save to CSV
csv_file_path = 'species_threats.csv'
with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=['species', 'threat_level'])
    writer.writeheader()
    writer.writerows(species_data)

print(f"Saved {len(species_data)} records to {csv_file_path}")