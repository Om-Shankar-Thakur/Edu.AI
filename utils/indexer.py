# utils/indexer.py
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from config.config import settings
import logging

logger = logging.getLogger(__name__)


def get_qdrant_client():
    url = settings.QDRANT_URL
    api_key = settings.QDRANT_API_KEY or None
    if url and url.startswith("http"):
        return QdrantClient(url=url, api_key=api_key)
    return QdrantClient()


def ensure_collection(vector_size: int):
    client = get_qdrant_client()
    try:
        client.get_collection(settings.COLLECTION_NAME)
        logger.info("Collection exists: %s", settings.COLLECTION_NAME)
    except Exception:
        logger.info("Creating collection: %s", settings.COLLECTION_NAME)
        client.recreate_collection(
            collection_name=settings.COLLECTION_NAME,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
        )


def upsert_batch(batch_vectors, batch_payloads, start_id=0):
    client = get_qdrant_client()
    points = []
    for i, (vec, meta) in enumerate(zip(batch_vectors, batch_payloads)):
        points.append(PointStruct(id=start_id + i, vector=vec, payload=meta))
    client.upsert(collection_name=settings.COLLECTION_NAME, points=points)


def search_vector(vector, top_k=5):
    client = get_qdrant_client()
    hits = client.search(collection_name=settings.COLLECTION_NAME,
                         query_vector=vector, limit=top_k, with_payload=True)
    result = []
    for h in hits:
        result.append({"id": h.id, "score": h.score, "payload": h.payload})
    return result
