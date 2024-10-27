# src/answer_generation/generate_answer.py

import requests
import json  # Import the json module for parsing

def initialize_ollama_connection(base_url="http://localhost:11434"):
    return base_url

def generate_answer(base_url, question, llm_model):
    prompt = f"""
### Task:
{question}

### Expected Output:
Python code that accomplishes the task.
"""
    payload = {
        "model": llm_model,
        "prompt": prompt,
        "stream":False  # Expecting JSON response
    }

    try:
        # Send request to Ollama API
        response = requests.post(f"{base_url}/api/generate", json=payload)
        response.raise_for_status()
        
        # Return the response text directly
        return response.text

    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Ollama API: {e}")
        return "Error connecting to Ollama API."

    except Exception as e:
        print(f"Unexpected error: {e}")
        return "Error: Unexpected response format from Ollama API."

