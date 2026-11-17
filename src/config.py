from pathlib import Path
import os

ROOT = Path(__file__).resolve().parents[1]
DOCUMENTOS = ROOT / 'data' / 'documentos'
CATALOGO = ROOT / 'data' / 'tablas' / 'catalogo_productos_2026_11.xlsx'
CHROMA_PATH = ROOT / 'data' / 'chroma'
COLLECTION_NAME = 'banco_nebula'
EMBEDDING_MODEL = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
OLLAMA_URL = os.environ.get('OLLAMA_URL', 'http://127.0.0.1:11434')
LLM_MODEL = os.environ.get('OLLAMA_MODEL', 'qwen2.5:7b')
