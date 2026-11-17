from src.chunking import dividir_seccion
from src.documentos import cargar_todo
from src.rag import es_historica


def test_carga_documentos():
    docs = cargar_todo()
    assert len([d for d in docs if d['metadatos']['tipo'] == 'xlsx']) == 4
    assert len([d for d in docs if d['metadatos']['tipo'] == 'txt']) >= 19
    assert all(d['metadatos']['doc_id'] for d in docs)


def test_chunking_sin_perdida():
    texto = ' '.join(str(i) for i in range(120))
    fragmentos = dividir_seccion(texto, 50, 10)
    reconstruido = fragmentos[0].split()
    for parte in fragmentos[1:]: reconstruido.extend(parte.split()[10:])
    assert reconstruido == texto.split()


def test_busqueda_historica():
    assert es_historica('¿Qué cambió entre 2025 y 2026?')
    assert not es_historica('¿Cuál es la cuota inicial vigente?')
