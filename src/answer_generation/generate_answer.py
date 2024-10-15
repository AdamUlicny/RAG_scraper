# src/answer_generation/generate_answer.py

import requests
import json  # Import the json module for parsing

def initialize_ollama_connection(base_url="http://localhost:11434"):
    return base_url

def generate_answer(base_url, question, context):
    prompt = f"JSON only response: Answer the question based on the provided context.\n\nContext:\n{context}\n\nQuestion: {question}\nAnswer:"
    payload = {
        "model": "qwen2.5:latest",  # Replace with the specific model you are using
        "prompt": prompt,
        "format": "json",
        "stream":False  # Expecting JSON response
    }

    try:
        response = requests.post(f"{base_url}/api/generate", json=payload)
        response.raise_for_status()

        # Parse the response as JSON
        result = json.loads(response.text)
        return result.get('response', "No answer found.")  # Adjust the key based on the actual response structure

    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Ollama API: {e}")
        return "Error generating answer."

    except json.JSONDecodeError:
        print("Failed to decode JSON:", response.text)
        return "Error: Unexpected response format from Ollama API."
