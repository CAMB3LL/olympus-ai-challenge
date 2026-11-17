from src.documentos import cargar_todo
from src.busqueda import indexar


def main():
    docs = cargar_todo()
    print(f'Fragmentos generados: {len(docs)}')
    print('Generando embeddings locales (el primer uso descarga el modelo)...')
    n = indexar(docs)
    print(f'✅ ChromaDB listo. Fragmentos indexados: {n}')


if __name__ == '__main__':
    main()
