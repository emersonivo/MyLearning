#!/usr/bin/env python3
"""
Vector Retriever using SentenceTransformers + ChromaDB.
Baseline RAG retrieval component.
"""

from sentence_transformers import SentenceTransformer
import chromadb
from typing import List, Dict, Any

class VectorRetriever:
    def __init__(self, model_name='all-MiniLM-L6-v2', collection_name='documents'):
        self.embedding_model = SentenceTransformer(model_name)
        self.client = chromadb.Client()
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"})

    def add_documents(self, documents: List[Dict[str, Any]]):
        texts = [doc['text'] for doc in documents]
        embeddings = self.embedding_model.encode(texts, show_progress_bar=True, batch_size=32)
        ids = [doc.get('id', f"doc_{i}") for i, doc in enumerate(documents)]
        metadatas = [doc.get('metadata', {}) for doc in documents]
        self.collection.add(embeddings=embeddings.tolist(), documents=texts,
                            ids=ids, metadatas=metadatas)
        print(f"[+] Added {len(documents)} documents")

    def search(self, query: str, top_k=5, filter_metadata=None) -> List[Dict]:
        query_emb = self.embedding_model.encode([query])
        where = filter_metadata if filter_metadata else None
        results = self.collection.query(query_embeddings=query_emb.tolist(),
                                        n_results=top_k, where=where)
        return [{'text': doc, 'score': 1 - dist, 'metadata': meta}
                for doc, dist, meta in zip(results['documents'][0],
                                           results['distances'][0],
                                           results['metadatas'][0])]

    def get_stats(self) -> dict:
        return {'total_documents': self.collection.count()}
