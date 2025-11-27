# File Search Engine

A powerful local file search engine with a modern React frontend and FastAPI backend.

## Features

- **Smart Search**: Semantic search using embeddings to find relevant documents even if keywords don't match exactly.
- **AI Summaries**: Automatically generates summaries for search results using OpenAI or local LLMs.
- **Modern UI**: Apple-style aesthetic with dark/light mode, smooth animations, and responsive design.
- **Auto-Indexing**: Automatically keeps your search index up to date.
- **Flexible Configuration**: Choose between OpenAI or local LLMs (via llama.cpp/GGUF).

## Prerequisites

- Python 3.8+
- Node.js 16+
- `pip` and `npm`

## Installation

1.  **Backend Setup**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Frontend Setup**:
    ```bash
    cd frontend
    npm install
    ```

## Running the Application

1.  **Start the Backend**:
    ```bash
    uvicorn api:app --reload
    ```
    The API will run at `http://localhost:8000`.

2.  **Start the Frontend**:
    ```bash
    cd frontend
    npm run dev
    ```
    The UI will run at `http://localhost:5173`.

3.  **Open the App**:
    Open your browser and navigate to `http://localhost:5173`.

## Configuration

- Click the **Settings** (gear icon) in the UI.
- Set the **Folder to Index**.
- Choose your **LLM Provider** (OpenAI or Local).
- If using OpenAI, provide your API Key.
- If using Local, provide the path to your GGUF model.
- Click **Save** and then **Trigger Re-indexing**.

## Legacy GUI

The old PySimpleGUI application has been renamed to `legacy_gui.py`. You can still run it if needed:
```bash
python legacy_gui.py
```
