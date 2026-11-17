"""Validaciones SIN modelos y SIN internet."""
from src.documentos import cargar_todo
from src.chunking import dividir_seccion


def main():
    docs = cargar_todo()
    txt = [d for d in docs if d['metadatos']['tipo'] == 'txt']
    xls = [d for d in docs if d['metadatos']['tipo'] == 'xlsx']
    print('--- VALIDACIÓN DE INGESTA ---')
    print(f'TXT: {len(txt)} | Excel: {len(xls)} | Total: {len(docs)}')
    assert len(xls) == 4, 'El catálogo debería tener 4 productos'
    assert any(d['metadatos']['estado'] == 'OBSOLETO' for d in docs)
    assert any(d['metadatos']['doc_id'] == 'POL-CVH-2026' for d in docs)
    assert all(len(d['contenido'].split()) <= 110 for d in docs)
    prueba = ' '.join('palabra' + str(i) for i in range(120))
    trozos = dividir_seccion(prueba, max_palabras=50, solapamiento=10)
    reconstruccion = trozos[0].split()
    for trozo in trozos[1:]: reconstruccion.extend(trozo.split()[10:])
    assert reconstruccion == prueba.split()
    print('✅ Documentos, metadatos y chunking validados')


if __name__ == '__main__':
    main()
