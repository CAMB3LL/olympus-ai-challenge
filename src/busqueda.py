"""Implementar embeddings, almacenamiento y recuperación vectorial.

Contrato requerido:
- indexar(documentos): agrega los documentos a la colección de Chroma y devuelve su cantidad.
- buscar(pregunta, k, incluir_obsoletos): devuelve una lista ordenada de hallazgos.

Cada hallazgo debe tener: contenido (str), metadatos (dict), distancia (float).
La función cliente_chroma() está suministrada para simplificar el arranque.
"""
from src.config import CHROMA_PATH, COLLECTION_NAME, EMBEDDING_MODEL


def cliente_chroma():
    import chromadb
    CHROMA_PATH.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(CHROMA_PATH))


def indexar(documentos: list[dict]) -> int:
    """Generar embeddings, persistirlos en Chroma, devolver cantidad indexada.

    TODO: usar el mismo modelo para documentos y consultas. Preservar texto/metadatos.
    """
    raise NotImplementedError('Implementar indexar() en src/busqueda.py')


def buscar(pregunta: str, k: int = 7, incluir_obsoletos: bool = False) -> list[dict]:
    """Recuperar hasta k fragmentos relevantes, filtrando obsoletos si corresponde.

    TODO: recuperar texto, metadatos y distancia en orden de relevancia.
    """
    raise NotImplementedError('Implementar buscar() en src/busqueda.py')
