from qdrant_client import QdrantClient
from qdrant_client.http import models as rest_models
from src.common.config import settings
from src.common.logger import get_logger

logger = get_logger("vector_store")

class VectorStore:
    def __init__(self):
        self.host = settings.qdrant_host
        self.port = settings.qdrant_port
        self.collection_name = settings.collection_name
        self.client = None
        self._init_client()

    def _init_client(self):
        try:
            # Try Docker local instance
            self.client = QdrantClient(host=self.host, port=self.port, timeout=2.0)
            # Query status to trigger connection attempt
            self.client.get_collections()
            logger.info(f"Successfully connected to Qdrant at {self.host}:{self.port}")
        except Exception:
            logger.warn(f"Failed to connect to Qdrant at {self.host}:{self.port}. Falling back to In-Memory mode.")
            # Fallback to local memory storage for test independence
            self.client = QdrantClient(":memory:")

    def create_collection_if_not_exists(self, vector_size: int = 1536):
        try:
            collections = self.client.get_collections().collections
            collection_names = [c.name for c in collections]
            if self.collection_name not in collection_names:
                self.client.recreate_collection(
                    collection_name=self.collection_name,
                    vectors_config=rest_models.VectorParams(
                        size=vector_size,
                        distance=rest_models.Distance.COSINE
                    )
                )
                logger.info(f"Collection '{self.collection_name}' created successfully with vector size {vector_size}.")
        except Exception as e:
            logger.error(f"Failed to create collection: {e}")

    def upsert_chunks(self, ids: list[int], vectors: list[list[float]], payloads: list[dict]):
        points = [
            rest_models.PointStruct(
                id=idx,
                vector=vec,
                payload=pay
            )
            for idx, vec, pay in zip(ids, vectors, payloads)
        ]
        try:
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            logger.info(f"Upserted {len(points)} chunks into collection '{self.collection_name}'.")
        except Exception as e:
            logger.error(f"Error upserting vectors: {e}")

    def search_nearest(self, vector: list[float], top_k: int = 15) -> list[dict]:
        try:
            results = self.client.query_points(
                collection_name=self.collection_name,
                query=vector,
                limit=top_k
            )
            return [
                {
                    "score": r.score,
                    "payload": r.payload
                }
                for r in results.points
            ]
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return []
