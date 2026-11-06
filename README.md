# IAjedrez

**Para retomar el trabajo con otro agente:** leer primero [Continuidad para agentes](CONTINUIDAD_PARA_AGENTES.md), que resume el contexto, las decisiones vigentes, el estado técnico y las verificaciones.

## Diseño principal aprobado

La página principal (`/`) muestra directamente **`IAjedrez_prototipo_interactivo.html`**, conservando su diseño, con desplazamiento independiente en Jugadas y variantes y en el cuerpo de respuestas, mientras el tablero permanece fijo. Este diseño es la base obligatoria para los próximos cambios: conservar distribución, colores, tipografía, espaciado y componentes; las futuras ediciones se harán sobre sus elementos.

Para mostrarlo, inicia el servidor y abre http://127.0.0.1:8765. También puede abrirse el HTML directamente. `/prototype` conserva el acceso al mismo archivo. El prototipo utiliza sus ejemplos y respuestas simuladas originales.

La demostración funcional de la entrevista Timmy-t–Kuanynsh se conserva en **`/demo`**. Incluye la partida completa, relojes del PGN, ocho momentos, consultas por jugada y paso, retorno al análisis y práctica con movimientos legales. Su [guion](GUION_DEMOSTRACION.md) corresponde a esa ruta; sus consultas duran la sesión de la página. No requiere Stockfish, Ollama ni Internet para los tres recorridos. La trazabilidad está en [Investigación a interfaz](INVESTIGACION_A_INTERFAZ.md).

Las herramientas generales descritas debajo siguen disponibles en `/lab`; su integración con Stockfish/Ollama continúa pendiente de verificación real. Integrar los datos de la entrevista en el diseño aprobado queda para las próximas ediciones de sus elementos.

## Ejecutar (PowerShell)

```powershell
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
.venv/Scripts/python -m uvicorn app:app --host 127.0.0.1 --port 8765
```

Abre http://127.0.0.1:8765. El prototipo original está en `/prototype`.

## Stockfish y Ollama

Descarga y extrae [Stockfish](https://stockfishchess.org/download/). Configura en la misma terminal antes de iniciar el servidor:

```powershell
$env:STOCKFISH_PATH = 'C:\ruta\stockfish.exe'
$env:OLLAMA_MODEL = 'nombre-del-modelo-instalado'
```

Instala [Ollama](https://ollama.com), descarga el modelo elegido con `ollama pull NOMBRE` y ejecuta su servicio local. `ollama list` muestra los nombres instalados. La API usa `http://127.0.0.1:11434/api/chat`. La elección del modelo depende de RAM, GPU, licencia y calidad en español. Ollama es el runtime; la apertura y licencia de cada modelo se revisan por separado. No se incluyen ni descargan automáticamente ejecutables o pesos.

Sin Stockfish funcionan importación, navegación y movimientos legales. Sin Ollama funciona el motor, pero no el tutor. Los fallos muestran mensajes explícitos, sin respuestas simuladas.

## Implementado

- Importar línea principal de PGN estándar y cargar ejemplo.
- Movimientos legales con python-chess, enroque, captura al paso y promoción.
- Aprende: probar una variante, analizarla y volver sin modificar la partida.
- Motor UCI: tres variantes, profundidad y evaluación desde blancas; mate separado de centipeones. Búsqueda de 0,4 segundos por posición.
- Tutor con evidencia calculada en el servidor y consultas asociadas a posición y etapa.
- Guardar/restaurar estudio JSON: partida, variante activa y consultas. No hay guardado automático; las evaluaciones se recalculan.
- Cadena de cuatro etapas didácticas; no expone razonamiento interno del modelo.

## Plan para completar el producto

1. Resumen automático de errores de toda la partida: comparar evaluación antes/después desde el jugador que mueve, tratar mates separadamente, calibrar umbrales, añadir progreso y cancelación. Actualmente se analizan posiciones, no se genera esa tabla.
2. Generar conclusiones estructuradas por etapa y preguntas hijas con historial conversacional. Actualmente las consultas son independientes y se conservan bajo su posición.
3. Completar tabla de consejos por jugada y catálogo verificado de referencias por concepto. Actualmente son orientaciones y recursos generales.
4. Árbol persistente de múltiples variantes, PGN con comentarios/variaciones y base de datos. Actualmente hay una variante activa y línea principal.
5. Pruebas con usuarios: comprender un error, resolver una duda y regresar, comparar alternativas. Medir éxito, errores, tiempo y comprensión; afinar teclado y accesibilidad.
6. Antes de publicar: autenticación, límites, colas del motor, privacidad, licencias y despliegue. Esta versión es para uso local en loopback.

La descripción suministrada de los artículos orienta la interacción; no equivale a una revisión de sus textos completos. Se conservan descomposición de tareas, contexto por jugada, divulgación progresiva y exploración reversible.

## Arquitectura y pruebas

`static/`: interfaz sin framework. `app.py`: validación, motor y tutor. El navegador no determina legalidad ni aporta evaluaciones confiables. Los textos generados se escapan. Stockfish usa un proceso acotado y un bloqueo para evitar cálculos simultáneos.

```powershell
.venv/Scripts/python -m pip install -r requirements-dev.txt
.venv/Scripts/python -m pytest -q
node --check static/app.js
```

Stockfish y Ollama necesitan verificación con instalaciones reales. Las dependencias usan rangos compatibles; generar un lock al validar el entorno de distribución.

Fuentes: [python-chess UCI](https://python-chess.readthedocs.io/en/latest/engine.html), [Ollama Chat](https://docs.ollama.com/api/chat). Stockfish y python-chess tienen licencias GPL; revisar obligaciones antes de distribuir. No se asignó licencia al código propio.


Documento de seguimiento: [Alcance y contexto pendiente](ALCANCE_Y_CONTEXTO.md).
