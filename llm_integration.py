from langchain_community.llms import OpenAI, LlamaCpp
from langchain_community.embeddings import OpenAIEmbeddings, LlamaCppEmbeddings

def get_llm(provider, api_key=None, model_path=None):
    """
    Returns a language model instance based on the specified provider.
    """
    if provider == 'openai':
        if not api_key:
            raise ValueError("API key is required for OpenAI provider")
        return OpenAI(api_key=api_key)
    elif provider == 'local':
        if not model_path:
            raise ValueError("Model path is required for local provider")
        return LlamaCpp(model_path=model_path)
    else:
        raise ValueError("Invalid LLM provider")

def get_embeddings(provider, api_key=None, model_path=None):
    """
    Returns an embeddings model instance based on the specified provider.
    """
    if provider == 'openai':
        if not api_key:
            raise ValueError("API key is required for OpenAI provider")
        return OpenAIEmbeddings(api_key=api_key)
    elif provider == 'local':
        if not model_path:
            raise ValueError("Model path is required for local provider")
        return LlamaCppEmbeddings(model_path=model_path)
    else:
        raise ValueError("Invalid LLM provider")

def summarize(text, provider, api_key=None, model_path=None):
    """
    Summarizes the given text using the specified LLM provider.
    """
    try:
        llm = get_llm(provider, api_key, model_path)
        if llm:
            return llm(f"Summarize the following text:\n\n{text}")
        return "Error: Could not summarize text."
    except Exception as e:
        print(f"Error summarizing text: {e}")
        return "Error: Could not summarize text."

def get_tags(text, provider, api_key=None, model_path=None):
    """
    Generates tags for the given text using the specified LLM provider.
    """
    try:
        llm = get_llm(provider, api_key, model_path)
        if llm:
            return llm(f"Generate a list of comma-separated tags for the following text:\n\n{text}")
        return "Error: Could not generate tags."
    except Exception as e:
        print(f"Error generating tags: {e}")
        return "Error: Could not generate tags."
