import json
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

class VectorDBIndexer:
    def __init__(self, qdrant_url="http://localhost:6333", collection_name="autocad_expert"):
        self.client = QdrantClient(qdrant_url)
        self.collection_name = collection_name
        self.vector_size = 384  # MiniLM-L6-v2

    def create_collection(self):
        try:
            self.client.delete_collection(self.collection_name)
        except:
            pass  # Collection doesn't exist, that's fine
        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(size=self.vector_size, distance=Distance.COSINE)
        )

    def index_documents(self, indexed_docs_jsonl="indexed_docs.jsonl"):
        points = []
        with open(indexed_docs_jsonl) as f:
            for line in f:
                doc = json.loads(line)
                embedding = doc.pop('embedding')
                point = PointStruct(
                    id=hash(doc['id']) % (2**31),
                    vector=embedding,
                    payload=doc
                )
                points.append(point)
        self.client.upsert(collection_name=self.collection_name, points=points)
        print(f"✓ Indexed {len(points)} points into Qdrant")

if __name__ == "__main__":
    idx = VectorDBIndexer()
    idx.create_collection()
    idx.index_documents()
