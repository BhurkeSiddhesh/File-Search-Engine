import os
import faiss
import pickle
import numpy as np
from langchain_text_splitters import CharacterTextSplitter
from llm_integration import get_embeddings, get_tags
from file_processing import extract_text

def create_index(folder_path, provider, api_key=None, model_path=None):
    """
    Creates a FAISS index for the files in the specified folder.
    """
    embeddings_model = get_embeddings(provider, api_key, model_path)
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)

    docs = []
    filepaths = []
    for dirpath, _, filenames in os.walk(folder_path):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            text = extract_text(filepath)
            if text:
                chunks = text_splitter.split_text(text)
                docs.extend(chunks)
                filepaths.extend([filepath] * len(chunks))

    if not docs:
        return None, None, None

    embeddings = np.array(embeddings_model.embed_documents(docs)).astype('float32')

    tags = get_tags("\n".join(docs), provider, api_key, model_path).split(',')

    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)

    return index, docs, tags

def save_index(index, docs, tags, filepath):
    """
    Saves the FAISS index and documents to a file.
    """
    faiss.write_index(index, filepath)
    with open('docs.pkl', 'wb') as f:
        pickle.dump(docs, f)
    with open('tags.pkl', 'wb') as f:
        pickle.dump(tags, f)

def load_index(filepath):
    """
    Loads a FAISS index and documents from a file.
    """
    index = faiss.read_index(filepath)
    with open('docs.pkl', 'rb') as f:
        docs = pickle.load(f)
    with open('tags.pkl', 'rb') as f:
        tags = pickle.load(f)
    return index, docs, tags
