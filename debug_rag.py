import os
import sys

print(f"Python executable: {sys.executable}")
print("Attempting to import llama_cpp...")

try:
    from llama_cpp import Llama
    print("Successfully imported Llama from llama_cpp")
except ImportError as e:
    print(f"Failed to import llama_cpp: {e}")
    sys.exit(1)
except Exception as e:
    print(f"Other error during import: {e}")
    sys.exit(1)

model_path = "models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
if not os.path.exists(model_path):
    # Try to find any model
    if os.path.exists("models"):
        files = os.listdir("models")
        gguf_files = [f for f in files if f.endswith(".gguf")]
        if gguf_files:
            model_path = os.path.join("models", gguf_files[0])
            print(f"Found model at: {model_path}")
        else:
            print("No GGUF models found in models/ directory")
            sys.exit(1)
    else:
        print("models/ directory does not exist")
        sys.exit(1)

print(f"Loading model from {model_path}...")
try:
    llm = Llama(model_path=model_path, verbose=True)
    print("Model loaded successfully!")
    
    print("Running inference...")
    output = llm("Q: Name the planets in the solar system? A: ", max_tokens=32, stop=["Q:", "\n"], echo=False)
    print(f"Output: {output}")
except Exception as e:
    print(f"Error during model load/inference: {e}")
