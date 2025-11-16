from sentence_transformers import SentenceTransformer

# Load model once globally (efficient)
_model = SentenceTransformer("all-MiniLM-L6-v2")


def embed_texts(texts):
    """
    Generate embeddings for a list of texts using SentenceTransformers.
    Used by both ingestion and retrieval to keep things consistent.
    """
    if isinstance(texts, str):
        texts = [texts]

    embeddings = _model.encode(
        texts,
        batch_size=64,
        show_progress_bar=False
    )

    return embeddings.tolist()


def embed_single(text: str):
    """
    Embed a single text string.
    """
    return _model.encode([text], show_progress_bar=False)[0].tolist()
