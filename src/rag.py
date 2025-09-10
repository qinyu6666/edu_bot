import os, pickle, faiss
from sentence_transformers import SentenceTransformer

class RAG:
    def __init__(self):
        self.index = faiss.read_index("vector_db/faiss.index")
        with open("vector_db/chunks.pkl", "rb") as f:
            self.chunks = pickle.load(f)
        self.model = SentenceTransformer("BAAI/bge-small-zh")
    def search(self, query, k=3):
        qv = self.model.encode([query], normalize_embeddings=True).astype('float32')
        scores, idxs = self.index.search(qv, k)
        return [self.chunks[i].page_content for i in idxs[0]]
