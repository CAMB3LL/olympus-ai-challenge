"""Orquestación de la búsqueda y generación; completar la implementación."""
import re
from src.busqueda import buscar
from src.llm import generar


def es_historica(pregunta: str) -> bool:
    """Heurística inicial proporcionada, puede modificarse si se justifica."""
    return bool(re.search(
        r'\b2025\b|hist[oó]ric|obsolet|versi[oó]n|compar|cambi[oó]|diferencia',
        pregunta.lower()
    ))


def preguntar(pregunta: str, k: int = 7) -> dict:
    """Devolver {pregunta, respuesta, fuentes_recuperadas}.

    TODO: orquestar la búsqueda y el modelo; manejar preguntas sin respuesta,
    versiones documentales y errores de componentes.
    `fuentes_recuperadas` debe ser una lista de objetos con campos:
       id, archivo, estado, distancia, fragmento.
    """
    raise NotImplementedError('Implementar preguntar() en src/rag.py')
