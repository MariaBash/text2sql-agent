import json
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

class RAGLoader:
    def __init__(self, examples_path: str = "data/rag_examples.json"):
        self.model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
        
        with open(examples_path, "r", encoding="utf-8") as f:
            self.examples = json.load(f)
        
        self.questions = [ex["question"] for ex in self.examples]
        self.embeddings = self.model.encode(self.questions, normalize_embeddings=True)
        
        self.index = faiss.IndexFlatIP(self.embeddings.shape[1])
        self.index.add(self.embeddings.astype("float32"))

    def retrieve(self, query: str, k: int = 5) -> list[dict]:
        """Возвращает топ-k похожих примеров"""
        query_emb = self.model.encode([query], normalize_embeddings=True)
        _, indices = self.index.search(query_emb.astype("float32"), k)
        return [self.examples[i] for i in indices[0]]