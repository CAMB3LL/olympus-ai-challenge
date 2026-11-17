# Olympus AI Engineering Challenge — Banco Nébula

**Desarrollado por Arley Calderón**

## Bienvenidos al desafío

Banco Nébula es un banco ficticio que necesita un asistente de inteligencia artificial para consultar sus políticas, productos y procedimientos. En este repositorio encontrarán una aplicación base y un conjunto de documentos sintéticos. El reto consiste en completar el núcleo de recuperación y generación de respuestas para que el asistente pueda responder con información verificable.

El enfoque es **RAG (Retrieval-Augmented Generation)**: primero se recuperan fragmentos documentales relevantes y luego un modelo de lenguaje genera una respuesta basada en ellos. No hace falta desarrollar una interfaz gráfica; la API incluye Swagger.

## Tecnologías

- Python 3.12; FastAPI y Uvicorn para la API HTTP.
- ChromaDB, mediante `PersistentClient`, para almacenar localmente fragmentos, metadatos y embeddings. No requiere instalar un servidor Chroma separado.
- `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` para representar documentos y preguntas como vectores.
- Ollama para ejecutar localmente el LLM `qwen2.5:7b`.
- `openpyxl` para los datos tabulares y `pytest` para pruebas automatizadas.

## Qué está preparado y qué falta

**Ya está disponible:** la lectura de archivos TXT y XLSX, extracción de metadatos, división de documentos en fragmentos, estructura de la API, configuración, scripts y pruebas iniciales. En `src/busqueda.py` también está preparada la creación del cliente local de ChromaDB.

**Deben completar principalmente:**

1. **`src/busqueda.py`:** generar embeddings, indexar y recuperar fragmentos por similitud; preservar texto, metadatos y vigencias; evitar duplicados al reindexar.
2. **`src/llm.py`:** construir el contexto con los fragmentos recuperados, consultar Qwen a través de Ollama y producir respuestas fundamentadas, sin inventar datos ausentes.
3. **`src/rag.py`:** coordinar búsqueda y generación, gestionar preguntas históricas o sin evidencia, y devolver el contrato definido.

Pueden modificar otros módulos si mantienen el comportamiento público de la API y explican sus decisiones.

## Contratos de integración

- `indexar(documentos: list[dict]) -> int`: almacena los fragmentos y devuelve el total indexado.
- `buscar(pregunta: str, k: int = 7, incluir_obsoletos: bool = False) -> list[dict]`: entrega hallazgos ordenados con `contenido`, `metadatos` y `distancia`.
- `generar(pregunta: str, hallazgos: list[dict]) -> str`: genera una respuesta en español basada en evidencia documental.
- `preguntar(pregunta: str, k: int = 7) -> dict`: entrega `pregunta`, `respuesta` y `fuentes_recuperadas`. Cada fuente debe contener `id`, `archivo`, `estado`, `distancia` y `fragmento`.

La API ofrece:

| Método | Ruta | Propósito |
| --- | --- | --- |
| GET | `/health` | Estado del servicio y cantidad de fragmentos indexados |
| POST | `/ask` | Responder una pregunta: `{"pregunta":"¿Qué exige el crédito de vivienda?","k":7}` |
| POST | `/batch` | Procesar varias preguntas: `{"preguntas":["Pregunta 1","Pregunta 2"],"k":7}` |

El indicador `/health` **no** garantiza que Ollama esté disponible ni que el RAG funcione correctamente.

## Preparar el entorno (Windows / PowerShell)

Instalar previamente **Python 3.12** y **Ollama** desde sus fuentes oficiales. Desde la raíz del proyecto:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Descargar y comprobar el LLM local:

```powershell
ollama pull qwen2.5:7b
ollama list
```

Precargar el modelo de embeddings (es distinto de Qwen):

```powershell
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')"
```

No se necesita crear manualmente una base de datos ChromaDB: la dependencia se instala con `requirements.txt` y los datos persistentes se crean en `data/chroma/` cuando se implemente la indexación.

## Verificar y ejecutar

Antes de completar los módulos pendientes, pueden verificar los insumos y la estructura:

```powershell
python -m scripts.validar_datos
python -m pytest -q
```

Las pruebas incluidas verifican la base del proyecto; **no** comprueban que el RAG esté terminado. Es esperado que la indexación y las consultas fallen mientras sigan los `TODO`.

Después de implementar la solución:

```powershell
python -m scripts.indexar
python -m uvicorn src.api:app --reload
```

Abrir `http://127.0.0.1:8000/docs` para utilizar Swagger. También se pueden ejecutar preguntas públicas y guardar los resultados:

```powershell
python -m scripts.probar_preguntas
```

## Comportamientos esperados

El asistente debe responder preguntas sobre los documentos TXT y el catálogo XLSX; diferenciar políticas vigentes y obsoletas; permitir comparaciones históricas cuando correspondan; identificar las fuentes que sustentan sus respuestas; reconocer información no disponible y manejar errores de manera comprensible.

No es obligatorio usar un framework de orquestación concreto. Una solución clara, reproducible y bien argumentada vale más que incorporar dependencias sin necesidad.

## Recursos y entrega

Pueden consultar documentación técnica, referencias de bibliotecas y utilizar herramientas convencionales de programación y depuración. **No utilizar asistentes generativos para diseñar, escribir, explicar o depurar el código** (ChatGPT, Copilot, Claude, Gemini u otros). Utilizar **Qwen como componente de la aplicación** sí forma parte del desafío.

Entregar un repositorio con el código ejecutable, instrucciones para reproducirlo, una explicación breve de arquitectura y decisiones tomadas, evidencia de pruebas y limitaciones conocidas. No subir `.venv`, modelos descargados, índices generados (`data/chroma/`), resultados de ejecución, credenciales ni archivos de caché.

La documentación y los datos incluidos son ficticios; no incorporar información bancaria real ni datos personales de clientes.

¡Éxitos con el desafío!
