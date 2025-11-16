# utils/ingest_courses.py

import pandas as pd
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
from tqdm import tqdm
import os
import pandas as pd

from config.config import settings
from models.embeddings import embed_texts   # <-- using the shared embedding function

COLLECTION = settings.COLLECTION_NAME


def get_qdrant_client():
    url = os.getenv("QDRANT_URL", settings.QDRANT_URL)
    api_key = os.getenv("QDRANT_API_KEY", settings.QDRANT_API_KEY) or None

    if url and url.startswith("http"):
        return QdrantClient(url=url, api_key=api_key)
    return QdrantClient()


def ingest(cleaned_csv_path: str, batch_size: int = 256):
    df = pd.read_csv(cleaned_csv_path)
    print(f"Loaded {len(df)} rows from {cleaned_csv_path}")

    qdrant = get_qdrant_client()

    # sample vector size
    sample_vec = embed_texts("test")[0]
    vector_size = len(sample_vec)

    # recreate collection if not exists
    try:
        qdrant.get_collection(COLLECTION)
    except Exception:
        print("Creating collection:", COLLECTION)
        qdrant.recreate_collection(
            collection_name=COLLECTION,
            vectors_config=VectorParams(
                size=vector_size,
                distance=Distance.COSINE
            ),
        )

    meta_fields = [c for c in df.columns if c != "embedding_text"]

    for start in range(0, len(df), batch_size):
        end = min(start + batch_size, len(df))
        batch = df.iloc[start:end]

        texts = batch["embedding_text"].astype(str).tolist()

        # use external embedding module
        embeddings = embed_texts(texts)

        points = []
        for i, (emb, (_, row)) in enumerate(zip(embeddings, batch.iterrows())):
            payload = {k: (None if pd.isna(row[k]) else row[k]) for k in meta_fields}

            # include final_url if present
            if "final_url" in row and pd.notna(row["final_url"]):
                payload["final_url"] = row["final_url"]

            points.append(
                PointStruct(
                    id=start + i,
                    vector=emb,
                    payload=payload
                )
            )

        qdrant.upsert(collection_name=COLLECTION, points=points)
        print(f"Upserted points {start}..{end-1}")

    print("Ingestion finished.")
