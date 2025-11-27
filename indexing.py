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

    # Generate tags for each document separately
    tags = []
    for doc in docs:
        doc_tags = get_tags(doc, provider, api_key, model_path)
        # Split the tags and clean them
        doc_tags_list = [tag.strip() for tag in doc_tags.split(',') if tag.strip()]
        # Use the first few tags or join them as needed
        tags.append(doc_tags_list[:5] if doc_tags_list else [])  # Limit to first 5 tags per doc

    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)

    return index, docs, tags

def save_index(index, docs, tags, filepath):
    """
    Saves the FAISS index and documents to a file.
    """
    import os
    faiss.write_index(index, filepath)
    docs_path = os.path.splitext(filepath)[0] + '_docs.pkl'
    tags_path = os.path.splitext(filepath)[0] + '_tags.pkl'
    with open(docs_path, 'wb') as f:
        pickle.dump(docs, f)
    with open(tags_path, 'wb') as f:
        pickle.dump(tags, f)

def load_index(filepath):
    """
    Loads a FAISS index and documents from a file.
    """
    import os
    index = faiss.read_index(filepath)
    docs_path = os.path.splitext(filepath)[0] + '_docs.pkl'
    tags_path = os.path.splitext(filepath)[0] + '_tags.pkl'
    with open(docs_path, 'rb') as f:
        docs = pickle.load(f)
    with open(tags_path, 'rb') as f:
        tags = pickle.load(f)
    return index, docs, tags
