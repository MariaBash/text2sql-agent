import hashlib
import json
import numpy as np
import psycopg2
from sentence_transformers import SentenceTransformer
import faiss

class CacheManager:
    def __init__(self, db_params: dict):
        self.db_params = db_params
        self.model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
        
        self.embedding_dim = 384
        self.index = faiss.IndexFlatIP(self.embedding_dim)  # Inner Product = cosine после нормализации
        self.questions = []      # для отладки
        self.sqls = []           # храним sql
        self.hashes = []         # для быстрого поиска
        
        self._load_cache_into_memory()

    def _normalize(self, question: str) -> str:
        return " ".join(question.strip().lower().split())

    def _get_hash(self, question: str) -> str:
        return hashlib.sha256(self._normalize(question).encode()).hexdigest()

    def _load_cache_into_memory(self):
        """Загружаем весь кэш в память при старте (он маленький)"""
        with psycopg2.connect(**self.db_params) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT question_hash, original_question, sql_query, embedding 
                    FROM sql_cache 
                    ORDER BY created_at
                """)
                for row in cur.fetchall():
                    q_hash, q_text, sql, emb_bytes = row
                    if emb_bytes:
                        emb = np.frombuffer(emb_bytes, dtype=np.float32)
                        self.index.add(emb.reshape(1, -1))
                        self.questions.append(q_text)
                        self.sqls.append(sql)
                        self.hashes.append(q_hash)

    def get_cached_sql(self, question: str) -> str | None:
        q_hash = self._get_hash(question)
        
        # 1. Точный поиск по хэшу (самый быстрый)
        with psycopg2.connect(**self.db_params) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT sql_query FROM sql_cache WHERE question_hash = %s", (q_hash,))
                row = cur.fetchone()
                if row:
                    # увеличиваем счётчик попаданий
                    cur.execute("UPDATE sql_cache SET hits = hits + 1 WHERE question_hash = %s", (q_hash,))
                    conn.commit()
                    return row[0]

        # 2. Семантический поиск (если точного нет)
        if len(self.questions) == 0:
            return None

        query_emb = self.model.encode([question], normalize_embeddings=True)
        distances, indices = self.index.search(query_emb.astype("float32"), 1)
        
        best_score = distances[0][0]
        if best_score >= 0.93:  # порог очень высокий — почти одинаковый смысл
            best_sql = self.sqls[indices[0][0]]
            # увеличиваем hits
            best_hash = self.hashes[indices[0][0]]
            with psycopg2.connect(**self.db_params) as conn:
                with conn.cursor() as cur:
                    cur.execute("UPDATE sql_cache SET hits = hits + 1 WHERE question_hash = %s", (best_hash,))
                    conn.commit()
            return best_sql

        return None

    def save_to_cache(self, question: str, sql: str):
        q_hash = self._get_hash(question)
        embedding = self.model.encode([question], normalize_embeddings=True)[0]
        
        with psycopg2.connect(**self.db_params) as conn:
            with conn.cursor() as cur:
                try:
                    cur.execute("""
                        INSERT INTO sql_cache 
                        (question_hash, original_question, sql_query, embedding)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (question_hash) DO NOTHING
                    """, (q_hash, question, sql, embedding.tobytes()))
                    conn.commit()
                    
                    # Добавляем в память
                    self.index.add(embedding.reshape(1, -1))
                    self.questions.append(question)
                    self.sqls.append(sql)
                    self.hashes.append(q_hash)
                except Exception as e:
                    print(f"Cache save error: {e}")