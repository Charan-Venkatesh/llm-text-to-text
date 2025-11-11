import json
import re
from sentence_transformers import SentenceTransformer

class FeatureExtractor:
    def __init__(self, embedding_model="sentence-transformers/all-MiniLM-L6-v2"):
        self.encoder = SentenceTransformer(embedding_model)
        self.chunk_size = 500
        self.chunk_overlap = 50

    def chunk_text(self, text):
        tokens = text.split()
        return [' '.join(tokens[i:i + self.chunk_size])
                for i in range(0, len(tokens), self.chunk_size - self.chunk_overlap)]

    def extract_features(self, chunk):
        features = {}
        features['has_code'] = 1 if '```' in chunk else 0
        features['command_count'] = len(re.findall(r'\b(PLOT|FILLET|LAYER)\b', chunk, re.IGNORECASE))
        features['embedding'] = self.encoder.encode(chunk, convert_to_numpy=True).tolist()
        return features

    def process_corpus(self, corpus_jsonl="autocad_corpus.jsonl"):
        indexed_docs = []
        with open(corpus_jsonl) as f:
            for line in f:
                doc = json.loads(line)
                for idx, chunk in enumerate(self.chunk_text(doc['text'])):
                    features = self.extract_features(chunk)
                    record = {
                        'id': f"{doc['id']}_chunk_{idx}",
                        'title': doc['title'],
                        'text': chunk,
                        'embedding': features['embedding'],
                        'has_code': features['has_code'],
                        'command_count': features['command_count'],
                        'source_url': doc['source_url'],
                        'tags': doc['tags']
                    }
                    indexed_docs.append(record)
        with open("indexed_docs.jsonl", "w") as f:
            for doc in indexed_docs:
                f.write(json.dumps(doc) + "\n")
        print(f"✓ Saved {len(indexed_docs)} chunks to indexed_docs.jsonl")

if __name__ == "__main__":
    extractor = FeatureExtractor()
    extractor.process_corpus()
