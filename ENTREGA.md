# Entrega — Asistente bancario RAG | Banco Nébula

## 1. Resumen

Esta solución implementa un asistente bancario basado en RAG (Retrieval-Augmented Generation) para consultar documentación ficticia de Banco Nébula.

El sistema:

- Procesa documentos TXT y un catálogo Excel.
- Divide los documentos en fragmentos.
- Genera embeddings con Sentence Transformers.
- Guarda y consulta los vectores en ChromaDB.
- Recupera fragmentos vigentes relevantes.
- Envía el contexto recuperado a Qwen mediante Ollama.
- Expone respuestas mediante una API FastAPI.
- Diferencia documentos vigentes, históricos y obsoletos.
- Reconoce consultas para las que no existe información suficiente.

## 2. Arquitectura

### Componentes principales

- `src/ingesta.py`: carga y procesa los documentos TXT.
- `src/ingesta_excel.py`: carga el catálogo de productos desde Excel.
- `src/documentos.py`: reúne todos los documentos para indexación.
- `src/chunking.py`: divide secciones extensas en fragmentos con solapamiento.
- `src/busqueda.py`: genera embeddings, crea el índice en ChromaDB y realiza búsquedas vectoriales.
- `src/llm.py`: comunica la pregunta y el contexto recuperado con Ollama/Qwen.
- `src/rag.py`: orquesta la recuperación y la generación de la respuesta.
- `src/api.py`: expone los servicios REST con FastAPI.
- `scripts/indexar.py`: genera el índice vectorial.
- `scripts/probar_preguntas.py`: ejecuta las preguntas públicas y guarda los resultados.
- `scripts/validar_datos.py`: verifica la ingesta y el chunking.

### Flujo de consulta

1. El usuario realiza una petición a `POST /ask` o `POST /batch`.
2. `src/rag.py` detecta si la consulta es histórica o actual.
3. `src/busqueda.py` genera el embedding de la pregunta.
4. ChromaDB recupera los fragmentos relevantes.
5. Las consultas actuales excluyen los fragmentos obsoletos.
6. Las consultas históricas o comparativas permiten recuperar también documentos obsoletos.
7. `src/llm.py` envía el contexto a Ollama/Qwen.
8. La API devuelve la respuesta y las fuentes recuperadas.

### Modelo de embeddings

- Modelo: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
- Base vectorial: ChromaDB persistente
- Colección: `banco_nebula`
- Ruta del índice: `data/chroma/`

La carpeta `data/chroma/` es un resultado generado y debe poder reconstruirse mediante `python -m scripts.indexar`.

### Modelo generativo

- Motor: Ollama
- Modelo: `qwen2.5:7b`
- API local predeterminada: `http://127.0.0.1:11434`

## 3. Ejecución en macOS

### Requisitos previos

- Python 3.12
- Ollama
- Conexión a internet durante la primera descarga del modelo de embeddings

### Preparar Python

```bash
cd /Users/cami/Desktop/ulthar/addagio/olympus-ai-challenge
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Preparar Ollama

```bash
ollama serve
```

En otra terminal:

```bash
ollama pull qwen2.5:7b
ollama list
```

Comprobación opcional:

```bash
ollama run qwen2.5:7b
```

Para salir:

```text
/bye
```

### Validar los datos

```bash
python -m scripts.validar_datos
python -m pytest -q
```

### Descargar el modelo de embeddings

```bash
python -c "from sentence_transformers import SentenceTransformer; m=SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'); print(m.encode('prueba').shape)"
```

### Generar el índice

```bash
python -m scripts.indexar
```

### Iniciar la API

```bash
python -m uvicorn src.api:app --reload
```

Documentación Swagger:

- <http://127.0.0.1:8000/docs>
- Health: <http://127.0.0.1:8000/health>

## 4. Ejemplos de uso

### Health check

```bash
curl http://127.0.0.1:8000/health
```

### Consulta individual

```bash
curl -X POST "http://127.0.0.1:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "pregunta": "¿Cuál es la cuota inicial mínima del Crédito Horizonte vigente?",
    "k": 7
  }'
```

### Consulta histórica o comparativa

```bash
curl -X POST "http://127.0.0.1:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "pregunta": "¿Qué diferencia hay entre las políticas de crédito de vivienda de 2025 y 2026?",
    "k": 10
  }'
```

### Consultas por lote

```bash
curl -X POST "http://127.0.0.1:8000/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "preguntas": [
      "¿Qué requisitos tiene la Cuenta Brisa?",
      "¿Cuál es el plazo máximo del crédito de vivienda?"
    ],
    "k": 7
  }'
```

## 5. Evidencias obtenidas

### Entorno

- Python utilizado: `3.12.16`
- ChromaDB instalado: `1.5.9`
- Modelo Ollama: `qwen2.5:7b`
- API disponible en `http://127.0.0.1:8000`

### Validación inicial

```text
TXT: 19 | Excel: 4 | Total: 23
✅ Documentos, metadatos y chunking validados
```

### Pruebas automatizadas

```text
3 passed
```

### Construcción del índice

```text
Fragmentos generados: 23
✅ ChromaDB listo. Fragmentos indexados: 23
```

### Health check

```json
{
  "status": "ok",
  "fragmentos_indexados": 23
}
```

### Preguntas públicas

Las diez preguntas públicas fueron ejecutadas mediante:

```bash
python -m scripts.probar_preguntas
```

Los resultados se guardan en `data/resultados/`.

Los resultados públicos más recientes son:

- `data/resultados/resultados_20261117_173352.json`

También se conservaron respuestas individuales de las pruebas HTTP realizadas en la entrega:

- `evidencia_consulta_vigente.json`: consulta vigente sobre requisitos y plazo del Crédito Horizonte.
- `evidencia_consulta_historica.json`: comparación de las políticas de crédito de vivienda de 2025 y 2026.
- `evidencia_sin_informacion.json`: consulta sobre una tasa futura que no está documentada.
- `evidencia_batch.json`: ejecución conjunta de dos consultas mediante `POST /batch`.

Casos especialmente validados:

- Consulta vigente sobre cuota inicial.
- Comparación histórica entre 2025 y 2026.
- Consulta estructurada del catálogo Excel.
- Consulta sobre OTP y seguridad digital.
- Consulta condicional para persona independiente.
- Reconocimiento de información futura no disponible.
- Reconocimiento de comisiones no documentadas.

## 6. Evidencias generadas y pendientes

Evidencias generadas:

- [x] Health check con `fragmentos_indexados: 23`.
- [x] Consulta vigente guardada en `evidencia_consulta_vigente.json`.
- [x] Consulta histórica guardada en `evidencia_consulta_historica.json`.
- [x] Consulta sin información guardada en `evidencia_sin_informacion.json`.
- [x] Resultado de `POST /batch` guardado en `evidencia_batch.json`.
- [x] Ejecución de las diez preguntas públicas guardada en `data/resultados/resultados_20261117_173352.json`.
- [ ] Capturas visuales opcionales de Swagger si el formato de entrega las requiere.
- [ ] Revisión manual final y firma del contenido de las diez respuestas públicas.
- [ ] Prueba recreando el índice desde cero, si aún no fue ejecutada.

Resultado resumido de las evidencias:

| Evidencia | Resultado |
| --- | --- |
| Validación de datos | 19 TXT + 4 Excel = 23 fragmentos |
| Pruebas automatizadas | 3 aprobadas |
| Índice ChromaDB | 23 fragmentos indexados |
| Health check | `status: ok` |
| Consulta vigente | Plazo 240 meses y requisitos documentados |
| Consulta histórica | Diferencias 2025/2026 recuperadas desde fuentes vigentes e obsoletas |
| Información ausente | Respuesta de abstención para la tasa de 2027 |
| Batch | Dos consultas procesadas correctamente |

## 7. Prueba recreada desde cero

Comando recomendado para demostrar reconstruibilidad:

```bash
rm -rf data/chroma
python -m scripts.indexar
python -m uvicorn src.api:app --host 127.0.0.1 --port 8000
```

Para evitar el recargador automático durante las pruebas finales, se recomienda iniciar la API sin `--reload`.

Resultado esperado:

```text
Fragmentos generados: 23
✅ ChromaDB listo. Fragmentos indexados: 23
```

## 8. Decisiones técnicas

### Embeddings

MiniLM se utiliza tanto para convertir los fragmentos como para convertir las preguntas. Esto permite que las consultas se comparen dentro del mismo espacio vectorial.

### Identificadores únicos

Los fragmentos reciben IDs SHA-256 derivados de su documento, fuente, sección, subfragmento y contenido. Los reindexados emplean `upsert`, evitando duplicados al repetir el proceso.

### Vigencia

Las consultas ordinarias excluyen fragmentos cuyo estado es `OBSOLETO`. Las consultas que mencionan 2025, historial, versiones, cambios o comparaciones pueden incluir documentos históricos.

Los documentos Excel tienen el estado `VIGENTE EN EL PERÍODO`, por lo que la búsqueda los trata como vigentes dentro del periodo documentado.

### Abstención

Si no se recuperan fragmentos válidos, el sistema no intenta responder con conocimiento general y informa que no existe información suficiente.

El prompt de Ollama también ordena no inventar datos ni presentar documentos históricos como vigentes.

## 9. Limitaciones conocidas

- La detección histórica es principalmente basada en palabras clave y años explícitos.
- La relevancia depende de la calidad del modelo MiniLM.
- La recuperación no realiza re-ranking semántico adicional.
- Ollama debe estar ejecutándose para que `generar()` funcione.
- La API devuelve error si Ollama no está disponible o supera el tiempo de espera.
- El modelo generativo puede utilizar más fragmentos de los que realmente necesita; las fuentes devuelven los fragmentos recuperados, no necesariamente un recorte perfecto de los citados.
- La primera descarga de MiniLM puede tardar varios minutos y necesita acceso de red.
- Las preguntas futuras o fuera del periodo documentado pueden recuperarse por cercanía vectorial, pero el prompt busca abstenerse cuando no existe soporte.

## 10. Posibles mejoras

- Implementar re-ranking de los fragmentos recuperados.
- Incorporar filtrado por metadatos de vigencia y fecha.
- Mejorar el detector de consultas históricas con clasificación semántica.
- Añadir pruebas automáticas para `buscar()`, `generar()` y `preguntar()`.
- Añadir pruebas de integración para Ollama y ChromaDB.
- Permitir configuración de `k` y umbral mínimo de distancia.
- Registrar trazas de recuperación y tiempos de respuesta.
- Agregar pruebas de prompts y respuestas adversariales.
- Separar mejor los fragmentos recuperados de las fuentes citadas efectivamente.

## 11. Archivos no incluidos en la entrega

No deben entregarse:

- `.venv/`
- `.cache/`
- `data/chroma/`
- Modelos descargados
- Credenciales
- Cachés de Python
- Archivos temporales

El índice debe poder reconstruirse a partir de los documentos originales mediante `scripts/indexar.py`.

## 12. Entrega del código

El reto queda implementado en los módulos:

- `src/busqueda.py`
- `src/llm.py`
- `src/rag.py`

La entrega incluye, junto con el código:

- Evidencia de instalación y ejecución.
- Evidencia de las pruebas automáticas.
- Evidencias de consultas vigentes e históricas.
- Evidencia de manejo de información insuficiente.
- Evidencia de ejecución de `POST /batch`.
- Respuestas JSON exportadas:
  - `evidencia_consulta_vigente.json`
  - `evidencia_consulta_historica.json`
  - `evidencia_sin_informacion.json`
  - `evidencia_batch.json`
- Los resultados generados por `scripts/probar_preguntas.py`, especialmente `data/resultados/resultados_20261117_173352.json`.
