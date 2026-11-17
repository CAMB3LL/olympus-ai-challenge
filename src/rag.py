"""Orquestación de la búsqueda y generación del asistente RAG."""
import re

from src.busqueda import buscar
from src.llm import generar


def es_historica(pregunta: str) -> bool:
    """Detecta preguntas que requieren comparar o consultar versiones históricas."""
    return bool(re.search(
        r'\b2025\b|hist[oó]ric|obsolet|versi[oó]n|compar|cambi[oó]|diferencia|antes|sustitu',
        pregunta.lower()
    ))


def preguntar(pregunta: str, k: int = 7) -> dict:
    """Busca documentación, genera una respuesta y devuelve sus fuentes."""
    if not isinstance(pregunta, str) or not pregunta.strip():
        raise ValueError('La pregunta no puede estar vacía')
    if not isinstance(k, int) or isinstance(k, bool) or k < 1:
        raise ValueError('k debe ser un entero positivo')

    incluir_obsoletos = es_historica(pregunta)
    consulta_ampliada = bool(re.search(
        r'cat[aá]logo|tabla|tasa|cuota|producto|catálogo|mensual|plazo máximo',
        pregunta.lower()
    ))

    cantidad_recuperacion = max(k * 2, 15) if consulta_ampliada else k
    hallazgos = buscar(
        pregunta,
        k=cantidad_recuperacion,
        incluir_obsoletos=incluir_obsoletos,
    )

    if consulta_ampliada:
        def prioridad(hallazgo: dict) -> tuple:
            metadatos = hallazgo.get('metadatos') or {}
            es_excel = str(metadatos.get('tipo', '')).lower() == 'xlsx'
            try:
                distancia = float(hallazgo.get('distancia', 0.0))
            except (TypeError, ValueError):
                distancia = 0.0
            return (0 if es_excel else 1, distancia)

        hallazgos = sorted(hallazgos, key=prioridad)[:k]

    fuentes = []
    hallazgos_validos = []
    for hallazgo in hallazgos:
        if not isinstance(hallazgo, dict):
            continue

        metadatos = hallazgo.get('metadatos') or {}
        estado = str(metadatos.get('estado') or 'SIN-ESTADO')

        # Una consulta actual nunca debe recuperar obsoletos; este filtro también
        # protege al RAG si el backend de búsqueda cambia su comportamiento.
        if not incluir_obsoletos and estado.upper() == 'OBSOLETO':
            continue

        hallazgos_validos.append(hallazgo)
        distancia = hallazgo.get('distancia', 0.0)
        try:
            distancia = float(distancia)
        except (TypeError, ValueError):
            distancia = 0.0

        fuentes.append({
            'id': str(metadatos.get('doc_id') or hallazgo.get('id') or 'SIN-ID'),
            'archivo': str(metadatos.get('fuente') or 'SIN-ARCHIVO'),
            'estado': estado,
            'distancia': distancia,
            'fragmento': str(hallazgo.get('contenido') or ''),
        })

    if not hallazgos_validos:
        respuesta = (
            'No encontré información suficiente en la documentación disponible '
            'para responder esta consulta.'
        )
    else:
        respuesta = generar(pregunta, hallazgos_validos)

    return {
        'pregunta': pregunta,
        'respuesta': respuesta,
        'fuentes_recuperadas': fuentes,
    }
