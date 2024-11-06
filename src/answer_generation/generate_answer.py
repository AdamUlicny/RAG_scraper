# src/answer_generation/generate_answer.py

import requests
import logging
import json

# Set up basic logging configuration (optional)
logging.basicConfig(level=logging.INFO)

def initialize_ollama_connection(base_url="http://localhost:11434"):
    """Initialize connection to Ollama API with given base URL."""
    return base_url

def generate_answer(base_url, question, llm_model):
    payload = {
        "model": llm_model,
        "prompt": question,
        "stream": False,
        "format": "json",
        "temperature": 0
    }

    try:
        response = requests.post(f"{base_url}/api/generate", json=payload)
        response.raise_for_status()
        
        # Assuming the API returns plain text as the answer.
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Ollama API: {e}")
        return "Error connecting to Ollama API."

    except json.JSONDecodeError:
        print("Failed to decode JSON:", response.text)
        return "Error: Unexpected response format from Ollama API."
