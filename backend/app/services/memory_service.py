import os
import uuid
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer

load_dotenv()

QDRANT_HOST = os.getenv("QDRANT_HOST", "qdrant")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))
COLLECTION = os.getenv("QDRANT_COLLECTION", "sentra_memory")
VECTOR_SIZE = 384  # all-MiniLM-L6-v2 output dimension

client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
embedder = SentenceTransformer("all-MiniLM-L6-v2")


def init_memory():
    existing = [c.name for c in client.get_collections().collections]
    if COLLECTION not in existing:
        client.create_collection(
            collection_name=COLLECTION,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
        )


def save_memory(task_id: str, filename: str, summary: str, anomalies: list):
    text = f"file: {filename}. anomalies: {', '.join(anomalies)}. summary: {summary}"
    vector = embedder.encode(text).tolist()
    point_id = abs(hash(task_id)) % (10 ** 9)
    client.upsert(
        collection_name=COLLECTION,
        points=[
            PointStruct(
                id=point_id,
                vector=vector,
                payload={
                    "task_id": task_id,
                    "filename": filename,
                    "anomalies": anomalies,
                    "summary": summary,
                },
            )
        ],
    )


def search_similar(query: str, limit: int = 3):
    vector = embedder.encode(query).tolist()
    results = client.search(
        collection_name=COLLECTION,
        query_vector=vector,
        limit=limit,
        with_payload=True,
    )
    return [{"score": r.score, **r.payload} for r in results]