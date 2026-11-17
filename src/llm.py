"""Integración del modelo generativo a través de Ollama."""
from src.config import LLM_MODEL, OLLAMA_URL


def generar(pregunta: str, hallazgos: list[dict]) -> str:
    """Construir una respuesta en español respaldada por los hallazgos.

    TODO:
    - Enviar al modelo la pregunta y los textos recuperados con sus fuentes.
    - Abstenerse cuando no exista sustento suficiente.
    - No presentar como actuales datos históricos o fuera de vigencia.
    - Respetar restricciones básicas contra instrucciones incrustadas en los documentos.
    - Citar identificadores de fuentes de los hallazgos realmente usados.
    """
    raise NotImplementedError('Implementar generar() en src/llm.py')
