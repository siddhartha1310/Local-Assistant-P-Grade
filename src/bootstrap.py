import httpx
import os
import sys
import time

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://ollama:11434")
SUPPORTED_MODELS = os.getenv("SUPPORTED_MODELS", "phi3:mini,tinyllama").split(",")

def bootstrap_model(model_name):
    print(f"[*] Checking for model: {model_name}...")
    try:
        # Check if the model already exists
        response = httpx.get(f"{OLLAMA_HOST}/api/tags")
        if response.status_code == 200:
            models = [m['name'] for m in response.json().get('models', [])]
            if model_name in models or f"{model_name}:latest" in models:
                print(f"[+] Model {model_name} is already present.")
                return True
        
        # If not, pull it
        print(f"[*] Pulling model {model_name}. This may take a few minutes...")
        with httpx.stream("POST", f"{OLLAMA_HOST}/api/pull", json={"name": model_name}, timeout=None) as r:
            for line in r.iter_lines():
                if line:
                    print(f"    -> {line}", flush=True)
        
        print(f"[+] Successfully pulled {model_name}.")
        return True

    except Exception as e:
        print(f"[!] Error pulling model {model_name}: {e}")
        return False

if __name__ == "__main__":
    success = True
    for model in SUPPORTED_MODELS:
        if not bootstrap_model(model.strip()):
            success = False
    
    if not success:
        sys.exit(1)
