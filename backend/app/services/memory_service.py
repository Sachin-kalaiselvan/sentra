from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

client = QdrantClient(url="http://localhost:6333")
COLLECTION = "sentra_memory"


def init_memory():
    collections = [c.name for c in client.get_collections().collections]
    if COLLECTION not in collections:
        client.create_collection(
            collection_name=COLLECTION,
            vectors_config=VectorParams(size=4, distance=Distance.COSINE)
        )


def save_memory(task_id: str, filename: str, anomaly_count: int):
    vector = [float(len(filename)), float(anomaly_count), 1.0, 0.5]
    client.upsert(
        collection_name=COLLECTION,
        points=[
            PointStruct(
                id=abs(hash(task_id)) % (10**9),
                vector=vector,
                payload={
                    "task_id": task_id,
                    "filename": filename,
                    "anomaly_count": anomaly_count,
                },
            )
        ],
    )


def search_similar(filename: str):
    vector = [float(len(filename)), 1.0, 1.0, 0.5]

    return client.query_points(
        collection_name=COLLECTION,
        query=vector,
        limit=3
    )