import faiss
import numpy as np

def search(query, index, docs, tags, embeddings_model):
    """
    Performs a semantic search on the index.
    """
    query_embedding = np.array([embeddings_model.embed_query(query)]).astype('float32')
    distances, indices = index.search(query_embedding, k=5) # Return top 5 results

    results = []
    for i, idx in enumerate(indices[0]):
        results.append({
            "document": docs[idx],
            "distance": distances[0][i],
            "tags": tags[idx] if idx < len(tags) else []
        })

    return results
