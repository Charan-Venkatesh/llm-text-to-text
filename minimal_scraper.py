import json
from datetime import datetime
import hashlib

SAMPLE_DOCS = [
    {
        "title": "PLOT Command - Autodesk Official",
        "text": "The PLOT command prints your drawing to a printer or file. Steps: 1) Type PLOT ...",
        "source_url": "https://help.autodesk.com/view/AUTOCAD/2025/ENU/?contextId=PLOT",
        "source_type": "official_docs",
        "tags": ["plot", "printing", "commands"]
    },
    # Add more sample docs, or extend by scraping if you wish
]

def create_corpus_file(output_path="autocad_corpus.jsonl"):
    with open(output_path, 'w') as f:
        for i, doc in enumerate(SAMPLE_DOCS):
            record = {
                "id": f"autocad_sample_{i:03d}",
                "title": doc["title"],
                "text": doc["text"],
                "source_url": doc["source_url"],
                "source_type": doc["source_type"],
                "tags": doc["tags"],
                "ingested_at": datetime.utcnow().isoformat(),
                "content_hash": hashlib.sha256(doc["text"].encode()).hexdigest()
            }
            f.write(json.dumps(record) + '\n')
    print(f"✓ Created corpus with {len(SAMPLE_DOCS)} documents at {output_path}")

if __name__ == "__main__":
    create_corpus_file()
