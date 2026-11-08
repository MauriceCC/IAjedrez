# IAjedrez

## Funciones restauradas

El inicio permite pegar PGN o adjuntar un archivo `.pgn` de hasta 100 KB, revisar su contenido y enviarlo al tablero. Los estudios importados se conservan en memoria hasta reiniciar el servidor (máximo 100). El análisis compara las decisiones blancas con Stockfish; las consultas usan Ollama mediante `OLLAMA_BASE_URL` y `OLLAMA_MODEL`, cargados automáticamente de `.env`. Las variables de la terminal tienen prioridad. Consulta `.env.example` para configurar el motor y el modelo.

El historial incluye Roni — Computer con tres consultas de ejemplo y una práctica guardada. Enter envía las consultas y Shift+Enter inserta un salto de línea. Las explicaciones del modelo pueden contener errores; las variantes se calculan con Stockfish. Se conservan las demás partidas y las mejoras de la tabla de evaluaciones.

**Historial precargado:** las tres partidas incluyen informes reales de Stockfish guardados en `data/history/`. Al abrirlas, la tabla se carga directamente sin recalcular la partida, incluso después de reiniciar el servidor. Cada informe conserva su fecha, motor y parámetros. Los cambios de PGN o parámetros invalidan el informe correspondiente; probar candidatas nuevas sigue requiriendo el motor.

**Tercer caso disponible (7 nov. 2026):** el historial del inicio incluye j017371–zhorzho11 y su conversación con Gemini. El estudio `/?game=gemini` verifica 34 decisiones blancas y dos decisiones negras con Stockfish, responde a las consultas sobre nivel, recomendaciones y notación, y ofrece práctica con recursos vinculados. Ver [síntesis y correcciones](static/conversacion-gemini.md). No requiere Ollama.

**Actualización vigente — Timmy-t–Kuanynsh (6 nov. 2026):** la página principal carga la partida y conversación aportadas (Lichess, 54 jugadas, 3+0). Contrasta las 54 decisiones blancas con Stockfish real y permite consultar 16.e4, 21.Te2, 29.Rf1 y 45.Cc7, reproducir variantes y practicar alternativas. Conserva el diseño aprobado. Ver [recorrido y resultados verificados](GUION_ENTREVISTA_STOCKFISH.md).

Stockfish 19 funciona en este equipo Windows desde `engines/stockfish/stockfish-windows-x86-64-universal.exe`, excluido de Git y detectado automáticamente. En otros equipos configura `STOCKFISH_PATH` o instala el motor en PATH. No es necesario Ollama. El estudio anterior descrito debajo permanece disponible en `/?game=mauricio`; `/demo` conserva la demostración preparada sin motor.

**Para retomar el trabajo con otro agente:** leer primero [Continuidad para agentes](CONTINUIDAD_PARA_AGENTES.md), que resume el contexto, las decisiones vigentes, el estado técnico y las verificaciones.

## Diseño principal aprobado

La página principal (`/`) muestra directamente **`IAjedrez_prototipo_interactivo.html`**, conservando su diseño, con desplazamiento independiente en Jugadas y variantes y en el cuerpo de respuestas, mientras el tablero permanece fijo. Este diseño es la base obligatoria para los próximos cambios: conservar distribución, colores, tipografía, espaciado y componentes; las futuras ediciones se harán sobre sus elementos.

La interfaz principal carga ahora **Mauricio0120 (783) — santoshglklklk (804)**, Chess.com, 26 de octubre de 2026, 5 minutos. Analiza las 19 decisiones de blancas con Stockfish real y contrasta la conversación aportada. [Guion de este recorrido](GUION_STOCKFISH.md).

- Escribe «¿Cuál fue mi error en esta partida?» o pulsa «Analizar mi partida». La primera revisión tarda alrededor de un minuto; las consultas posteriores reutilizan el análisis en memoria del servidor.
- Puedes preguntar por `9. Nd2` / `9. Cd2`, `9. Qf3` / `9. Df3`, el final tras `19…Rd2+` / `19…Td2+` y otras jugadas blancas concretas. Se admite la pregunta original con el PGN adjunto **de esta misma partida**. Un PGN distinto se rechaza explícitamente.
- La tabla muestra caídas estimadas, candidatas y evaluaciones desde blancas. Cadena permite volver al paso exacto; Aprende valida una candidata legal y la evalúa con el motor.
- Stockfish calcula; el tutor emplea **plantillas de alcance limitado**, sin LLM. Una consulta no reconocida se indica como no validada. Las etiquetas locales no equivalen a las clasificaciones de Chess.com.
- El PGN indica `0–1`, sin motivo de terminación. No se inventa abandono ni derrota por tiempo.

Usa el servidor local: el HTML ya requiere la API para cargar la partida. `/prototype` sirve la misma interfaz. La demo anterior de Timmy-t–Kuanynsh sigue en `/demo`, con su [guion de la entrevista](GUION_DEMOSTRACION.md) y sus respuestas preparadas. El laboratorio general permanece en `/lab`.

## Ejecutar en Linux

```bash
python3 -m venv venv
venv/bin/python -m pip install -r requirements-dev.txt
# Instala Stockfish desde el gestor de paquetes de tu sistema si falta.
# Si no está en PATH, indica el ejecutable:
export STOCKFISH_PATH=/usr/games/stockfish
venv/bin/python -m uvicorn app:app --host 127.0.0.1 --port 8765
```

Abre http://127.0.0.1:8765. Stockfish 16 está instalado y probado en el equipo actual. No se distribuye el binario en el repositorio. No necesitas Ollama para este recorrido.

## Ejecutar (PowerShell)

```powershell
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
.venv/Scripts/python -m uvicorn app:app --host 127.0.0.1 --port 8765
```

Abre http://127.0.0.1:8765. La misma interfaz está disponible en `/prototype`.

## Stockfish y Ollama (laboratorio `/lab`)

Descarga y extrae [Stockfish](https://stockfishchess.org/download/). Configura en la misma terminal antes de iniciar el servidor:

```powershell
$env:STOCKFISH_PATH = 'C:\ruta\stockfish.exe'
$env:OLLAMA_MODEL = 'nombre-del-modelo-instalado'
```

Instala [Ollama](https://ollama.com), descarga el modelo elegido con `ollama pull NOMBRE` y ejecuta su servicio local. `ollama list` muestra los nombres instalados. La API usa `http://127.0.0.1:11434/api/chat`. La elección del modelo depende de RAM, GPU, licencia y calidad en español. Ollama es el runtime; la apertura y licencia de cada modelo se revisan por separado. No se incluyen ni descargan automáticamente ejecutables o pesos.

Sin Stockfish funcionan importación, navegación y movimientos legales. Sin Ollama funciona el motor, pero no el tutor. Los fallos muestran mensajes explícitos, sin respuestas simuladas.

## Implementado en el laboratorio `/lab`

- Importar línea principal de PGN estándar y cargar ejemplo.
- Movimientos legales con python-chess, enroque, captura al paso y promoción.
- Aprende: probar una variante, analizarla y volver sin modificar la partida.
- Motor UCI: tres variantes, profundidad y evaluación desde blancas; mate separado de centipeones. Búsqueda de 0,4 segundos por posición.
- Tutor con evidencia calculada en el servidor y consultas asociadas a posición y etapa.
- Guardar/restaurar estudio JSON: partida, variante activa y consultas. No hay guardado automático; las evaluaciones se recalculan.
- Cadena de cuatro etapas didácticas; no expone razonamiento interno del modelo.

## Plan para completar el producto

El recorrido principal ya compara las decisiones blancas de la partida precargada. Los siguientes puntos corresponden a generalizar el laboratorio a partidas arbitrarias.

1. Resumen automático de errores de toda la partida: comparar evaluación antes/después desde el jugador que mueve, tratar mates separadamente, calibrar umbrales, añadir progreso y cancelación. Actualmente se analizan posiciones, no se genera esa tabla.
2. Generar conclusiones estructuradas por etapa y preguntas hijas con historial conversacional. Actualmente las consultas son independientes y se conservan bajo su posición.
3. Completar tabla de consejos por jugada y catálogo verificado de referencias por concepto. Actualmente son orientaciones y recursos generales.
4. Árbol persistente de múltiples variantes, PGN con comentarios/variaciones y base de datos. Actualmente hay una variante activa y línea principal.
5. Pruebas con usuarios: comprender un error, resolver una duda y regresar, comparar alternativas. Medir éxito, errores, tiempo y comprensión; afinar teclado y accesibilidad.
6. Antes de publicar: autenticación, límites, colas del motor, privacidad, licencias y despliegue. Esta versión es para uso local en loopback.

La descripción suministrada de los artículos orienta la interacción; no equivale a una revisión de sus textos completos. Se conservan descomposición de tareas, contexto por jugada, divulgación progresiva y exploración reversible.

## Arquitectura y pruebas

`review.py`: análisis, comparación de candidatas y consultas del recorrido. `static/review.js`: comportamiento del diseño aprobado. `static/`: interfaz sin framework. `app.py`: validación, motor y tutor. El navegador no determina legalidad ni aporta evaluaciones confiables. Los textos generados se escapan. Stockfish usa un proceso acotado y un bloqueo para evitar cálculos simultáneos.

```powershell
.venv/Scripts/python -m pip install -r requirements-dev.txt
.venv/Scripts/python -m pytest -q
node --check static/app.js
```

Verificación del recorrido principal:

```bash
venv/bin/python -m pytest -q
node --check static/review.js
venv/bin/python -m playwright install chromium --only-shell
# Con el servidor activo:
venv/bin/python tests/ui_review.py
```

El test UI envía la pregunta original y el PGN, consulta 9.Cd2 y 9.Df3, recorre la defensa del final, prueba candidatas con Stockfish y verifica retorno, desplazamiento y tablero fijo en escritorio y móvil. Las capturas se guardan en el directorio temporal del sistema.

Stockfish se verificó en el recorrido principal; Ollama sigue pendiente. Las dependencias usan rangos compatibles; generar un lock al validar el entorno de distribución.

Fuentes: [python-chess UCI](https://python-chess.readthedocs.io/en/latest/engine.html), [Ollama Chat](https://docs.ollama.com/api/chat). Stockfish y python-chess tienen licencias GPL; revisar obligaciones antes de distribuir. No se asignó licencia al código propio.


Documento de seguimiento: [Alcance y contexto pendiente](ALCANCE_Y_CONTEXTO.md).
