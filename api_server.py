from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient

app = FastAPI(title="AutoCAD Expert LLM")

embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
db = QdrantClient("http://localhost:6333")
collection_name = "autocad_expert"

class QueryRequest(BaseModel):
    question: str
    top_k: int = 3

@app.get("/")
async def root():
    return {
        "message": "AutoCAD Expert LLM API",
        "endpoints": {
            "GET /": "API info",
            "GET /health": "Health check",
            "POST /ask": "Ask a question",
            "GET /docs": "API documentation"
        }
    }

@app.post("/ask")
async def ask_question(req: QueryRequest):
    try:
        query_embedding = embedding_model.encode(req.question).tolist()
        results = db.search(collection_name=collection_name, query_vector=query_embedding, limit=req.top_k)
        
        if not results:
            return {"question": req.question, "answer": "No relevant documents found.", "sources": []}
        
        # Combine answers from top results
        answer = " ".join([res.payload['text'] for res in results])
        sources = [res.payload.get('source_url', 'Unknown') for res in results]
        
        return {"question": req.question, "answer": answer, "sources": sources}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    try:
        # Try to connect to Qdrant
        db.get_collections()
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        return {"status": "error", "database": "disconnected", "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
