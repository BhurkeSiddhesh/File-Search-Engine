from langchain_community.embeddings import OpenAIEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
try:
    from llama_cpp import Llama
except ImportError:
    Llama = None
import re
import os

# Cache for loaded models
_embeddings_cache = {}
_llm_cache = {}

def get_embeddings(provider, api_key=None, model_path=None):
    """Returns an embeddings model instance based on the provider."""
    cache_key = f"{provider}:{api_key or ''}"
    
    if cache_key in _embeddings_cache:
        return _embeddings_cache[cache_key]
    
    if provider == 'openai' and api_key:
        embeddings = OpenAIEmbeddings(api_key=api_key)
    else:
        print("Loading local embeddings...")
        embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        print("Embeddings loaded!")
    
    _embeddings_cache[cache_key] = embeddings
    return embeddings

def get_llm_model(model_path):
    """Load and cache the GGUF model."""
    if not Llama:
        print("llama_cpp not installed")
        return None
        
    if not model_path or not os.path.exists(model_path):
        print(f"Model not found at {model_path}")
        return None

    if model_path in _llm_cache:
        return _llm_cache[model_path]

    print(f"Loading LLM from {model_path}...")
    try:
        # Load with reasonable defaults for CPU inference
        llm = Llama(
            model_path=model_path,
            n_ctx=2048,  # Context window
            n_threads=4, # cpu threads
            verbose=False
        )
        _llm_cache[model_path] = llm
        print("LLM loaded!")
        return llm
    except Exception as e:
        print(f"Failed to load LLM: {e}")
        return None

def generate_ai_answer(context, question, model_path):
    """
    Generate a natural language answer using the local LLM.
    """
    llm = get_llm_model(model_path)
    if not llm:
        return None

    prompt = f"""System: You are a helpful AI assistant. Answer the question based ONLY on the provided context. If the answer is not in the context, say "I couldn't find the answer in the documents."
    
Context:
{context}

Question: {question}

Answer:"""

    try:
        # Use the new create_completion API for llama-cpp-python >= 0.3.x
        output = llm.create_completion(
            prompt,
            max_tokens=256,
            stop=["System:", "Question:", "Context:"],
            echo=False,
            temperature=0.3
        )
        return output['choices'][0]['text'].strip()
    except AttributeError:
        # Fallback for older versions - try direct call
        try:
            output = llm(
                prompt,
                max_tokens=256,
                stop=["System:", "Question:", "Context:"],
                echo=False,
                temperature=0.3
            )
            return output['choices'][0]['text'].strip()
        except Exception as e:
            print(f"Fallback generation error: {e}")
            return None
    except Exception as e:
        print(f"Generation error: {e}")
        return None

def extract_answer(text, question):
    """
    Legacy extraction: keyword matching fallback.
    """
    if not text or not question:
        return None
    
    # Extract key terms from the question
    question_lower = question.lower()
    
    # Remove question words
    cleaned_q = re.sub(r'\b(what|where|when|who|why|how|which|did|does|is|are|was|were)\b', '', question_lower)
    # Extract meaningful words (4+ chars)
    question_terms = [w for w in re.findall(r'\b[a-zA-Z]{3,}\b', cleaned_q) if w not in {'the', 'and', 'for', 'that', 'this'}]
    
    if not question_terms:
        return None
    
    # Split text into sentences
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    # Score each sentence based on keyword matches
    scored_sentences = []
    for sent in sentences:
        sent_lower = sent.lower()
        score = sum(1 for term in question_terms if term in sent_lower)
        if score > 0:
            scored_sentences.append((score, sent))
    
    # Sort by score and take best matches
    scored_sentences.sort(reverse=True, key=lambda x: x[0])
    
    # Return top 1-2 relevant sentences as the answer
    if scored_sentences:
        best_sentences = [s[1].strip() for s in scored_sentences[:2]]
        answer = ' '.join(best_sentences)
        # Truncate if too long
        if len(answer) > 300:
            answer = answer[:297] + "..."
        return answer
    
    return None

def summarize(text, provider, api_key=None, model_path=None, question=None):
    """
    Creates a summary. For answers, we now use generate_ai_answer in the main flow,
    but this remains as a per-document fallback/utility.
    """
    try:
        if question:
            answer = extract_answer(text, question)
            if answer:
                return answer
        
        # Extractive summary
        text = re.sub(r'\s+', ' ', text).strip()
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        summary_sentences = []
        for sent in sentences:
            if len(sent) > 30:
                summary_sentences.append(sent)
                if len(summary_sentences) >= 2:
                    break
        
        if summary_sentences:
            return ' '.join(summary_sentences)
        return text[:150] + "..." if len(text) > 150 else text
    except Exception as e:
        print(f"Error: {e}")
        return ""

def get_tags(text, provider, api_key=None, model_path=None):
    try:
        words = re.findall(r'\b[a-zA-Z]{4,15}\b', text.lower())
        stop_words = {
            'this', 'that', 'with', 'from', 'have', 'will', 'been', 'would',
            'could', 'should', 'their', 'there', 'about', 'which', 'these',
            'other', 'more', 'some', 'such', 'only', 'than', 'into', 'over'
        }
        words = [w for w in words if w not in stop_words]
        word_freq = {}
        for w in words:
            word_freq[w] = word_freq.get(w, 0) + 1
        top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]
        return ', '.join([w[0] for w in top_words])
    except Exception as e:
        return ""
