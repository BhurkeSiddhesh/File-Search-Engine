from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from indexing import create_index, save_index, load_index
from search import search
from llm_integration import summarize, get_embeddings
from file_processing import extract_text

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React development server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SearchRequest(BaseModel):
    query: str
    folder_path: str
    use_llm: bool = False

class SearchResult(BaseModel):
    file_path: str
    snippet: str
    summary: Optional[str] = None

@app.post("/api/search", response_model=List[SearchResult])
async def search_files(request: SearchRequest):
    try:
        # Load or create index
        try:
            index = load_index(request.folder_path)
        except:
            # If index doesn't exist, create it
            index = create_index(request.folder_path)
            save_index(index, request.folder_path)

        # Perform search
        results = search(request.query, index)
        
        # Process results
        search_results = []
        for file_path, snippet in results:
            result = SearchResult(
                file_path=file_path,
                snippet=snippet
            )
            if request.use_llm:
                # Get summary if LLM is enabled
                text = extract_text(file_path)
                result.summary = summarize(text)
            search_results.append(result)
            
        return search_results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/index")
async def index_folder(folder_path: str):
    try:
        index = create_index(folder_path)
        save_index(index, folder_path)
        return {"status": "success", "message": "Folder indexed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)