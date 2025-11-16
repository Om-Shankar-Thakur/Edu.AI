import os
from dotenv import load_dotenv
load_dotenv()

class Settings:
    HF_API_TOKEN = os.getenv("HF_API_TOKEN")
    QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
    QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    COLLECTION_NAME = os.getenv("COLLECTION_NAME", "courses_collection")
    TOP_K = int(os.getenv("TOP_K", "6"))
    MAX_CONTEXT_CHUNKS = int(os.getenv("MAX_CONTEXT_CHUNKS", "6"))
    HF_MODEL = os.getenv("HF_MODEL", "mistralai/mistral-7b-instruct")
    DEBUG = os.getenv("DEBUG", "True").lower() in ('true','1','yes')

settings = Settings()
