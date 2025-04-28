from langchain_ollama import ChatOllama

def initialize_ollama(api_key: str):
    """
    Initialize the Ollama client with the provided API key.
    
    :param api_key: Your Ollama API key.
    :return: An instance of the Ollama client.
    """
    return Ollama(api_key=api_key)

def generate_answer(ollama_client, prompt: str):
    """
    Generate an answer using the Ollama client.
    
    :param ollama_client: An instance of the Ollama client.
    :param prompt: The prompt to generate an answer for.
    :return: The generated answer.
    """
    response = ollama_client.generate(prompt)
    return response['text']

def main():
    api_key = "your_api_key_here"
    prompt = "What is the capital of France?"
    
    ollama_client = initialize_ollama(api_key)
    answer = generate_answer(ollama_client, prompt)
    
    print(f"Generated Answer: {answer}")

if __name__ == "__main__":
    main() 