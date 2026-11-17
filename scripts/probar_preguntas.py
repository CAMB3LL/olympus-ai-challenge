"""Ejecuta preguntas públicas y guarda respuestas SIN calificarlas automáticamente."""
import json
from datetime import datetime
from pathlib import Path
from src.rag import preguntar
from src.config import ROOT


def main():
    preguntas = json.loads((ROOT / 'data/preguntas/preguntas_publicas.json').read_text(encoding='utf-8'))
    resultados = []
    for item in preguntas:
        print(f"Procesando {item['id']}: {item['pregunta']}")
        respuesta = preguntar(item['pregunta'])
        resultados.append({'id': item['id'], **respuesta})
    salida = ROOT / 'data' / 'resultados'
    salida.mkdir(parents=True, exist_ok=True)
    nombre = salida / f"resultados_{datetime.now():%Y%m%d_%H%M%S}.json"
    nombre.write_text(json.dumps(resultados, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'✅ Respuestas guardadas en {nombre}')
    print('Revisá manualmente la calidad de las respuestas y sus fuentes.')


if __name__ == '__main__':
    main()
