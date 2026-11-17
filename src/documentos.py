"""Punto central para obtener el conjunto de chunks."""
from src.ingesta import cargar_txt
from src.ingesta_excel import cargar_excel


def cargar_todo() -> list[dict]:
    return cargar_txt() + cargar_excel()
