from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import os
import configparser
from indexing import create_index, save_index, load_index
from search import search
from llm_integration import summarize, get_embeddings
from file_processing import extract_text

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
index = None
docs = []
tags = []

def load_config():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config

def save_config_file(config):
    with open('config.ini', 'w') as configfile:
        config.write(configfile)

# Initialize index on startup if available
@app.on_event("startup")
async def startup_event():
    global index, docs, tags
    if os.path.exists('index.faiss'):
        try:
            index, docs, tags = load_index('index.faiss')
            print("Loaded existing index.")
        except Exception as e:
            print(f"Failed to load index: {e}")

class SearchRequest(BaseModel):
    query: str

class SearchResult(BaseModel):
    document: str
    summary: Optional[str] = None
    tags: List[str] = []

class ConfigModel(BaseModel):
    folder: str
    auto_index: bool
    openai_api_key: Optional[str] = ""
    local_model_path: Optional[str] = ""
    provider: str = "openai"

@app.get("/api/config")
async def get_config():
    config = load_config()
    return {
        "folder": config.get('General', 'folder', fallback=''),
        "auto_index": config.getboolean('General', 'auto_index', fallback=False),
        "openai_api_key": config.get('APIKeys', 'openai_api_key', fallback=''),
        "local_model_path": config.get('LocalLLM', 'model_path', fallback=''),
        "provider": config.get('LocalLLM', 'provider', fallback='openai')
    }

@app.post("/api/config")
async def update_config(config_data: ConfigModel):
    config = configparser.ConfigParser()
    config['General'] = {'folder': config_data.folder, 'auto_index': str(config_data.auto_index)}
    config['APIKeys'] = {'openai_api_key': config_data.openai_api_key or ''}
    config['LocalLLM'] = {'model_path': config_data.local_model_path or '', 'provider': config_data.provider}
    save_config_file(config)
    return {"status": "success", "message": "Configuration saved"}

@app.post("/api/search", response_model=List[SearchResult])
async def search_files(request: SearchRequest):
    global index, docs, tags
    
    if not index:
        raise HTTPException(status_code=400, detail="Index not loaded. Please configure and index a folder first.")

    try:
        config = load_config()
        provider = config.get('LocalLLM', 'provider', fallback='openai')
        api_key = config.get('APIKeys', 'openai_api_key', fallback=None)
        model_path = config.get('LocalLLM', 'model_path', fallback=None)
        
        embeddings_model = get_embeddings(provider, api_key, model_path)
        
        # Search
        results = search(request.query, index, docs, tags, embeddings_model)
        
        # Process results with summaries
        processed_results = []
        for result in results:
            summary = summarize(result['document'], provider, api_key, model_path)
            processed_results.append(SearchResult(
                document=result['document'],
                summary=summary,
                tags=result['tags']
            ))
            
        return processed_results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/index")
async def trigger_indexing(background_tasks: BackgroundTasks):
    config = load_config()
    folder = config.get('General', 'folder', fallback='')
    if not folder or not os.path.exists(folder):
        raise HTTPException(status_code=400, detail="Invalid folder path in configuration")
    
    background_tasks.add_task(run_indexing, config)
    return {"status": "accepted", "message": "Indexing started in background"}

def run_indexing(config):
    global index, docs, tags
    folder = config.get('General', 'folder')
    provider = config.get('LocalLLM', 'provider', fallback='openai')
    api_key = config.get('APIKeys', 'openai_api_key', fallback=None)
    model_path = config.get('LocalLLM', 'model_path', fallback=None)
    
    try:
        new_index, new_docs, new_tags = create_index(folder, provider, api_key, model_path)
        if new_index:
            save_index(new_index, new_docs, new_tags, 'index.faiss')
            index, docs, tags = new_index, new_docs, new_tags
            print("Indexing completed successfully.")
        else:
            print("Indexing failed or no documents found.")
    except Exception as e:
        print(f"Error during indexing: {e}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)