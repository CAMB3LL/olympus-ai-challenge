"""Embeddings, almacenamiento y recuperación vectorial con ChromaDB."""
import hashlib

from src.config import CHROMA_PATH, COLLECTION_NAME, EMBEDDING_MODEL


_EMBEDDINGS = None


def cliente_chroma():
    import chromadb

    CHROMA_PATH.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(CHROMA_PATH))


def _modelo_embeddings():
    global _EMBEDDINGS
    if _EMBEDDINGS is None:
        try:
            from sentence_transformers import SentenceTransformer

            _EMBEDDINGS = SentenceTransformer(EMBEDDING_MODEL)
        except Exception as exc:
            raise RuntimeError(
                f'No fue posible cargar el modelo de embeddings {EMBEDDING_MODEL}: {exc}'
            ) from exc
    return _EMBEDDINGS


def _metadatos_validos(metadatos: dict) -> dict:
    limpio = {}
    for clave, valor in metadatos.items():
        if valor is None:
            limpio[clave] = ''
        elif isinstance(valor, (str, int, float, bool)):
            limpio[clave] = valor
        else:
            limpio[clave] = str(valor)
    return limpio


def _id_fragmento(documento: dict) -> str:
    metadatos = documento.get('metadatos') or {}
    base = '|'.join([
        str(metadatos.get('doc_id', '')),
        str(metadatos.get('fuente', '')),
        str(metadatos.get('seccion', '')),
        str(metadatos.get('subfragmento', '')),
        str(documento.get('contenido', '')),
    ])
    return hashlib.sha256(base.encode('utf-8')).hexdigest()


def indexar(documentos: list[dict]) -> int:
    """Genera embeddings, realiza upsert en Chroma y devuelve documentos totales."""
    if not isinstance(documentos, list):
        raise ValueError('documentos debe ser una lista')

    cliente = cliente_chroma()
    coleccion = cliente.get_or_create_collection(name=COLLECTION_NAME)

    if not documentos:
        return coleccion.count()

    textos = []
    ids = []
    metadatos = []
    for documento in documentos:
        contenido = documento.get('contenido')
        if not isinstance(contenido, str) or not contenido.strip():
            continue

        metadatos_documento = _metadatos_validos(documento.get('metadatos') or {})
        textos.append(contenido)
        ids.append(_id_fragmento(documento))
        metadatos.append(metadatos_documento)

    if not textos:
        return coleccion.count()

    try:
        embeddings = _modelo_embeddings().encode(textos, normalize_embeddings=True)
    except RuntimeError:
        raise
    except Exception as exc:
        raise RuntimeError(f'No fue posible generar los embeddings: {exc}') from exc

    vectores = [vector.tolist() for vector in embeddings]
    coleccion.upsert(ids=ids, embeddings=vectores, documents=textos, metadatas=metadatos)
    return coleccion.count()


def buscar(pregunta: str, k: int = 7, incluir_obsoletos: bool = False) -> list[dict]:
    """Busca fragmentos relevantes y conserva texto, metadatos y distancia."""
    if not isinstance(pregunta, str) or not pregunta.strip():
        raise ValueError('La pregunta no puede estar vacía')
    if not isinstance(k, int) or isinstance(k, bool) or k < 1:
        raise ValueError('k debe ser un entero positivo')

    cliente = cliente_chroma()
    colecciones = {getattr(c, 'name', c): c for c in cliente.list_collections()}
    if COLLECTION_NAME not in colecciones:
        return []

    coleccion = cliente.get_collection(name=COLLECTION_NAME)
    if coleccion.count() == 0:
        return []

    try:
        vector = _modelo_embeddings().encode(
            pregunta, normalize_embeddings=True
        ).tolist()
    except RuntimeError:
        raise
    except Exception as exc:
        raise RuntimeError(f'No fue posible generar el embedding de la consulta: {exc}') from exc

    consulta = {
        'query_embeddings': [vector],
        'n_results': min(k, coleccion.count()),
        'include': ['documents', 'metadatas', 'distances'],
    }
    if not incluir_obsoletos:
        consulta['where'] = {'estado': {'$ne': 'OBSOLETO'}}

    try:
        resultado = coleccion.query(**consulta)
    except Exception as exc:
        raise RuntimeError(f'No fue posible consultar ChromaDB: {exc}') from exc

    ids = resultado.get('ids') or [[]]
    documentos = resultado.get('documents') or [[]]
    metadatas = resultado.get('metadatas') or [[]]
    distancias = resultado.get('distances') or [[]]

    hallazgos = []
    for id_fragmento, contenido, metadatos, distancia in zip(
        ids[0], documentos[0], metadatas[0], distancias[0]
    ):
        if metadatos is None:
            metadatos = {}
        hallazgos.append({
            'id': id_fragmento,
            'contenido': contenido,
            'metadatos': metadatos,
            'distancia': float(distancia),
        })
    return hallazgos
