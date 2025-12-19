import os
import requests
import threading

MODELS_DIR = "models"
os.makedirs(MODELS_DIR, exist_ok=True)

# Curated list of GGUF models
AVAILABLE_MODELS = [
    {
        "id": "tinyllama-1.1b-chat-v1.0.Q4_K_M",
        "name": "TinyLlama 1.1B Chat",
        "description": "Fast and lightweight, great for older hardware.",
        "size": "637 MB",
        "url": "https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
    },
    {
        "id": "phi-2.Q4_K_M",
        "name": "Phi-2 (Microsoft)",
        "description": "Microsoft's powerful small model (2.7B).",
        "size": "1.7 GB",
        "url": "https://huggingface.co/TheBloke/phi-2-GGUF/resolve/main/phi-2.Q4_K_M.gguf"
    },
    {
        "id": "mistral-7b-instruct-v0.1.Q4_K_M",
        "name": "Mistral 7B Instruct",
        "description": "High performance 7B model.",
        "size": "4.37 GB",
        "url": "https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF/resolve/main/mistral-7b-instruct-v0.1.Q4_K_M.gguf"
    }
]

download_status = {
    "downloading": False,
    "model_id": None,
    "progress": 0,
    "error": None
}

def get_available_models():
    return AVAILABLE_MODELS

def get_local_models():
    """Return list of downloaded models with path, name, and size."""
    models = []
    if os.path.exists(MODELS_DIR):
        for f in os.listdir(MODELS_DIR):
            if f.endswith(".gguf"):
                filepath = os.path.join(MODELS_DIR, f)
                size = os.path.getsize(filepath)
                models.append({
                    "id": f.replace(".gguf", ""),
                    "filename": f,
                    "path": os.path.abspath(filepath),
                    "size": size,
                    "name": f.replace(".gguf", "").replace("-", " ").replace(".", " ")
                })
    return models

def download_file(url, filename, model_id):
    global download_status
    filepath = os.path.join(MODELS_DIR, filename)
    
    try:
        print(f"Starting download: {url}")
        download_status = {"downloading": True, "model_id": model_id, "progress": 0, "error": None}
        
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024 * 1024  # 1MB
        downloaded = 0
        
        with open(filepath, 'wb') as file:
            for data in response.iter_content(block_size):
                downloaded += len(data)
                file.write(data)
                if total_size > 0:
                    download_status["progress"] = int((downloaded / total_size) * 100)
                    
        print(f"Download complete: {filename}")
        download_status = {"downloading": False, "model_id": None, "progress": 100, "error": None}
        
    except Exception as e:
        print(f"Download failed: {e}")
        download_status = {"downloading": False, "model_id": model_id, "progress": 0, "error": str(e)}
        # Clean up partial download
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
            except:
                pass

def start_download(model_id):
    global download_status
    
    if download_status["downloading"]:
        return False, "Another download is in progress"
    
    model = next((m for m in AVAILABLE_MODELS if m["id"] == model_id), None)
    if not model:
        return False, f"Model not found: {model_id}"
    
    filename = f"{model_id}.gguf"
    filepath = os.path.join(MODELS_DIR, filename)
    
    # Check if already downloaded
    if os.path.exists(filepath):
        return False, "Model already downloaded"
    
    thread = threading.Thread(target=download_file, args=(model["url"], filename, model_id))
    thread.daemon = True
    thread.start()
    return True, "Download started"

def get_download_status():
    return download_status

def delete_model(model_path):
    """Delete a downloaded model file."""
    if os.path.exists(model_path):
        os.remove(model_path)
        return True
    return False
