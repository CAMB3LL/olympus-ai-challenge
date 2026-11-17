def dividir_seccion(texto: str, max_palabras: int = 110, solapamiento: int = 15) -> list[str]:
    """Divide una sección extensa por palabras sin perder contenido.

    Se conservan palabras repetidas para contexto; versión educativa.
    """
    if max_palabras < 1 or not 0 <= solapamiento < max_palabras:
        raise ValueError('max_palabras debe ser positivo y solapamiento menor al máximo')
    palabras = texto.split()
    resultado = []
    inicio = 0
    while inicio < len(palabras):
        fin = min(inicio + max_palabras, len(palabras))
        resultado.append(' '.join(palabras[inicio:fin]))
        if fin == len(palabras):
            break
        inicio = fin - solapamiento
    return resultado
