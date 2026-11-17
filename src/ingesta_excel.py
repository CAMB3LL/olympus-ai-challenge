"""Transforma cada producto del catálogo Excel en un chunk independiente."""
from openpyxl import load_workbook
from src.config import CATALOGO


def cargar_excel() -> list[dict]:
    libro = load_workbook(CATALOGO, read_only=True, data_only=True)
    try:
        notas = libro['Vigencia_y_Notas']
        info = {}
        for fila in notas.iter_rows(min_row=4, values_only=True):
            campo, valor = (list(fila) + [None, None])[:2]
            if campo and valor is not None:
                info[str(campo)] = str(valor)
        resultado = []
        for fila in libro['Productos'].iter_rows(min_row=5, values_only=True):
            celdas = (list(fila) + [None] * 7)[:7]
            codigo, nombre, tipo, tasa, cuota, plazo, observacion = celdas
            if not codigo:
                continue
            contenido = (
                f'Producto: {nombre}\nCódigo: {codigo}\nTipo: {tipo}\n'
                f'Tasa efectiva anual (E.A.): {tasa} %\n'
                f'Cuota de manejo mensual: COP {cuota}\n'
                f'Plazo máximo: {plazo if plazo is not None else "No aplica"} meses\n'
                f'Observación: {observacion}\n'
                f'Vigencia de las tasas: {info["Fecha de inicio"]} a {info["Fecha de fin"]}'
            )
            resultado.append({
                'contenido': contenido,
                'metadatos': {
                    'doc_id': info['Identificador'],
                    'titulo': 'Catálogo de productos',
                    'version': '2026-11',
                    'estado': info['Estado'],
                    'vigencia': f'{info["Fecha de inicio"]} a {info["Fecha de fin"]}',
                    'fuente': CATALOGO.name,
                    'tipo': 'xlsx',
                    'seccion': str(codigo),
                    'titulo_seccion': str(nombre),
                    'subfragmento': 1,
                }
            })
        return resultado
    finally:
        libro.close()


if __name__ == '__main__':
    docs = cargar_excel()
    print(f'Productos: {len(docs)}')
    for d in docs[:2]: print(d)
