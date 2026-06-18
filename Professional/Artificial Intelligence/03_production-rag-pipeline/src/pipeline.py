#!/usr/bin/env python3
"""
Production RAG Pipeline.
Handles ingestion, chunking, embedding (with cache), and search.

Usage:
  from src.pipeline import ProductionPipeline
  pipeline = ProductionPipeline()
  pipeline.ingest('docs/manual.pdf')
  results = pipeline.search("How do I configure logging?")
"""

import json
import hashlib
from pathlib import Path
from typing import List, Dict
from sentence_transformers import SentenceTransformer
import chromadb

class ProductionPipeline:
    def __init__(self, cache_dir=".pipeline_cache", db_dir=".chromadb"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.client = chromadb.PersistentClient(path=db_dir)
        self.collection = self.client.get_or_create_collection(
            "production_rag", metadata={"hnsw:space": "cosine"})
        self.doc_index = self._load_index()

    def _load_index(self) -> dict:
        idx_file = self.cache_dir / "document_index.json"
        if idx_file.exists():
            return json.loads(idx_file.read_text())
        return {}

    def _save_index(self):
        (self.cache_dir / "document_index.json").write_text(
            json.dumps(self.doc_index, indent=2))

    def _hash_file(self, path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def _extract_text(self, file_path: Path) -> str:
        suffix = file_path.suffix.lower()
        if suffix == '.pdf':
            try:
                from pypdf import PdfReader
                return '\n\n'.join(p.extract_text() or '' for p in PdfReader(file_path).pages)
            except ImportError:
                return file_path.read_text(errors='ignore')
        elif suffix == '.docx':
            try:
                from docx import Document
                return '\n\n'.join(p.text for p in Document(file_path).paragraphs)
            except ImportError:
                return file_path.read_text(errors='ignore')
        elif suffix in ['.html', '.htm']:
            try:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(file_path.read_text(), 'html.parser')
                for s in soup(['script', 'style']): s.decompose()
                return soup.get_text(separator='\n')
            except ImportError:
                return file_path.read_text(errors='ignore')
        else:
            return file_path.read_text(errors='ignore')

    def _chunk_text(self, text: str, chunk_size=512, overlap=64) -> List[str]:
        words = text.split()
        chunks = []
        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            if chunk.strip():
                chunks.append(chunk)
        return chunks

    def ingest(self, file_path: str) -> int:
        path = Path(file_path)
        if not path.exists():
            print(f"[!] File not found: {file_path}")
            return 0
        file_hash = self._hash_file(path)
        doc_id = str(path)
        if doc_id in self.doc_index and self.doc_index[doc_id]['hash'] == file_hash:
            print(f"[*] Unchanged: {path.name} (skipped)")
            return 0
        print(f"[*] Ingesting: {path.name}")
        text = self._extract_text(path)
        chunks = self._chunk_text(text)
        print(f"    Created {len(chunks)} chunks")
        embeddings = self.embedding_model.encode(chunks, show_progress_bar=False)
        ids = [f"{doc_id}::chunk_{i}" for i in range(len(chunks))]
        metadatas = [{'source': str(path), 'chunk_idx': i} for i in range(len(chunks))]
        # Remove existing chunks for this doc if updating
        if doc_id in self.doc_index:
            old_ids = self.doc_index[doc_id].get('chunk_ids', [])
            if old_ids:
                self.collection.delete(ids=old_ids)
        self.collection.add(embeddings=embeddings.tolist(), documents=chunks,
                            ids=ids, metadatas=metadatas)
        self.doc_index[doc_id] = {'hash': file_hash, 'chunk_ids': ids,
                                   'chunk_count': len(chunks)}
        self._save_index()
        print(f"    Indexed {len(chunks)} chunks")
        return len(chunks)

    def search(self, query: str, top_k=5) -> List[Dict]:
        query_emb = self.embedding_model.encode([query])
        results = self.collection.query(query_embeddings=query_emb.tolist(), n_results=top_k)
        return [{'text': doc, 'source': meta.get('source', ''), 'score': 1 - dist}
                for doc, dist, meta in zip(results['documents'][0],
                                           results['distances'][0],
                                           results['metadatas'][0])]

    def get_statistics(self) -> dict:
        return {'total_documents': len(self.doc_index),
                'total_chunks': self.collection.count(),
                'indexed_files': list(self.doc_index.keys())}
