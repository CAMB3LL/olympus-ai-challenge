"""Lee los documentos TXT y conserva origen, estado y vigencia."""
import re
from src.config import DOCUMENTOS
from src.chunking import dividir_seccion

CAMPOS = ['ID', 'Título', 'Versión', 'Estado', 'Vigencia']


def cargar_txt() -> list[dict]:
    resultado = []
    for archivo in sorted(DOCUMENTOS.glob('*.txt')):
        texto = archivo.read_text(encoding='utf-8-sig')
        metadatos = {}
        for linea in texto.splitlines():
            for campo in CAMPOS:
                if linea.startswith(campo + ':'):
                    metadatos[campo] = linea.split(':', 1)[1].strip()
        # Cada sección numerada es una unidad semántica; se subdivide si es larga.
        partes = re.split(r'(?=^\d+\.\s+)', texto, flags=re.MULTILINE)
        for parte in partes:
            parte = parte.strip()
            m = re.match(r'^(\d+)\.\s+([^\n]+)', parte)
            if not m:
                continue  # El encabezado alimenta metadatos, no chunks.
            numero, titulo_seccion = m.group(1), m.group(2)
            for subnumero, contenido in enumerate(dividir_seccion(parte), start=1):
                resultado.append({
                    'contenido': contenido,
                    'metadatos': {
                        'doc_id': metadatos.get('ID','SIN-ID'),
                        'titulo': metadatos.get('Título',''),
                        'version': metadatos.get('Versión',''),
                        'estado': metadatos.get('Estado','SIN-ESTADO'),
                        'vigencia': metadatos.get('Vigencia',''),
                        'fuente': archivo.name,
                        'tipo': 'txt',
                        'seccion': numero,
                        'titulo_seccion': titulo_seccion,
                        'subfragmento': subnumero,
                    }
                })
    return resultado


if __name__ == '__main__':
    docs = cargar_txt()
    print(f'Fragmentos TXT: {len(docs)}')
    for d in docs[:2]: print(d)
