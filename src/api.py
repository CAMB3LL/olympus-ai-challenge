"""API de consulta; abrir http://127.0.0.1:8000/docs para Swagger."""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from src.rag import preguntar
from src.busqueda import cliente_chroma
from src.config import COLLECTION_NAME

app = FastAPI(title='Banco Nébula · AI Knowledge Assistant', version='0.1.0')


class Pregunta(BaseModel):
    pregunta: str = Field(min_length=1)
    k: int = Field(default=7, ge=1, le=15)


class Lote(BaseModel):
    preguntas: list[str] = Field(min_length=1, max_length=30)
    k: int = Field(default=7, ge=1, le=15)


@app.get('/health')
def salud():
    cliente = cliente_chroma()
    disponibles = cliente.list_collections()
    cantidad = cliente.get_collection(name=COLLECTION_NAME).count() if any(
        getattr(c, 'name', c) == COLLECTION_NAME for c in disponibles
    ) else 0
    return {'status': 'ok', 'fragmentos_indexados': cantidad}


@app.post('/ask')
def ask(req: Pregunta):
    try:
        return preguntar(req.pregunta, k=req.k)
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.post('/batch')
def batch(req: Lote):
    try:
        return {'resultados': [preguntar(p, k=req.k) for p in req.preguntas]}
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
