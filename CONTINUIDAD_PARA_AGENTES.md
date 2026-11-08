# Integración con la nueva interfaz

Se integraron las tarjetas Blancas/Negras y las descargas PGN/PNG de origin/main con la importación y Ollama. POST /api/review/import recibe player_color (white por defecto); Study analiza solo ese lado y compara las pérdidas con su signo correcto. Las puntuaciones siguen desde blancas. La práctica usa el turno de la posición; el tablero indica el lado analizado. Probado en navegador: adjunto nativo, negras, análisis, flechas, consulta real llama3.1:8b, práctica negra y descargas. Prueba de regresión: tests/test_player_color.py.

# Restauración de funciones

Se recuperaron .env/python-dotenv, Ollama en ambos tutores, importación de PGN por texto y archivo local, controles de adjunto, Enter/Shift+Enter y Roni con ejemplos guardados. Se integraron sobre la versión con Gemini y history_evidence sin eliminar esas mejoras. studies.py gestiona importaciones temporales; RONI_STUDY es permanente; static/roni-example.json conserva tres consultas y una práctica. API y pruebas: tests/test_generative.py, tests/test_roni.py, tests/ui_pgn_file.py y tests/ui_generative.py. Las respuestas guardadas identifican extractos y correcciones editoriales.

# Continuidad de IAjedrez para otros agentes

## Evaluación, tablas y flechas de variantes

«Consejos» se renombró «Evaluación» en los tres estudios. `static/evaluation-ui.js` comparte las tablas: Jugada abre Cadena; Consejo/Explicación/Jugada sugerida abren la candidata guardada conservando la pestaña. Resumen muestra la pérdida en Tipo y los valores del motor bajo jugada real y sugerida. Las explicaciones combinan motivos revisados de las conversaciones y descripciones limitadas de la variante calculada; no se inventan diagnósticos posicionales generales.

Tipos locales positivos: Mejor jugada si coincide con la primera candidata; Excelente si pierde hasta 10 cp; Buena si pierde menos de 50 cp. Se mantienen los umbrales de errores y tratamiento separado de mates. Brillante está documentada en la leyenda, pero no se asigna sin una validación específica del sacrificio: no equivale a tener puntuación alta ni a ser la mejor jugada.

Botones exteriores «/» llevan al inicio/final de la partida original incluso durante variantes o práctica. Las flechas interiores siguen recorriendo la variante activa. El SVG superpuesto usa azul para el movimiento mostrado y naranja discontinuo para el siguiente movimiento de la PV: no es un mapa completo de amenazas. Se elimina al volver a la partida. `tests/ui_evaluation.py` verifica ambos tipos de clic, navegación, puntuaciones, leyenda, flechas, retorno y móvil en los tres estudios con evidencia precargada.

## Historial con análisis persistente (7 nov. 2026)

Los tres informes reales de Stockfish se guardan en `data/history/{mauricio,entrevista,gemini}.json`. `history_evidence.py` valida versión, hash del PGN y parámetros de búsqueda antes de reutilizarlos. Incluyen nombre del motor, fecha original, variantes y profundidad real. La API de partida incluye el informe y el navegador muestra directamente la tabla, sin pedir un análisis nuevo. Las consultas reutilizan el mismo informe. Reiniciar el servidor no invalida estos resultados históricos; cambiar PGN o parámetros sí. La práctica de nuevas candidatas sigue usando Stockfish en vivo.

Para regenerar un informe después de cambios, ejecutar el analizador del módulo con Stockfish disponible y guardar el resultado mediante `history_evidence.save(nombre, pgn, review.DEPTH, review.SECONDS, informe)`. Si se desea recalcular sin cambiar PGN ni parámetros, retirar primero el archivo correspondiente. No modificar a mano sus evaluaciones. `tests/test_history_evidence.py` impide arrancar el motor y comprueba carga y consultas de los tres estudios, así como rechazo de evidencia obsoleta.

## Tercer estudio: conversación con Gemini (7 nov. 2026)

Se agregó `gemini` a la selección de estudios y al historial. Partida j017371–zhorzho11, 4 nov. 2026, 10 minutos, 67 medias jugadas, 1–0 sin motivo de terminación. PGN original con NAG en `static/partida-gemini.pgn`; síntesis atribuida en `static/conversacion-gemini.md`. La perspectiva es blancas, siguiendo la respuesta de Gemini; el usuario no identificó explícitamente su bando.

`gemini.py` calcula las 34 decisiones blancas y las decisiones negras 13…Cc5 y 25…Dxg5, manteniéndolas separadas de la clasificación de errores blancos. Las preguntas originales sobre nivel, aprendizaje y notación tienen respuestas preparadas con evidencia; una consulta desconocida no se presenta como validada. `static/gemini-ui.js` organiza resumen, consejos, temas de Aprende y referencias. No se integró Ollama ni Gemini en vivo.

Hallazgos observados con Stockfish 19, profundidad objetivo 19 / 1,5 s por búsqueda: 12.Cxd5 pasó de −1,03 a −6,86; 25.O-O de +6,67 a −2,85, con …Axf3 como respuesta calculada. Para negras, 13…Cc5 pasó de −7,44 a +5,91 y 25…Dxg5 de −3,32 a +9,61 (siempre perspectiva blanca). Son valores de una ejecución, no constantes del código. Destacan también 7.a3, 8.b4 y 9.b5. La continuación 26.Cxg5 Axd1 elimina ambas damas: el error de …Dxg5 no se explica como «dama gratis». El caballo estaba clavado relativamente a la dama d1 por el alfil g4. El último 34.Txf7 no es mate.

Notación: se corrige la mezcla de signos en Gemini. $4 = ??, $6 = ?!, $9 = peor jugada; se conservan como anotaciones del PGN, no conclusiones de Stockfish. Recursos gratuitos de Lichess vinculados a seguridad de piezas, clavadas, desarrollo y mates básicos; los últimos son entrenamiento futuro, no motivos que se afirme haber ocurrido.

Validación: `tests/test_gemini.py`, cuatro pruebas con motor real, legalidad de variantes, cambio de damas, consultas, PGN distinto y motor ausente. Playwright/Edge verificó historial, resumen automático, resultado correcto, variante, notación, Aprende, práctica/retorno y ancho móvil sin errores de JavaScript. Captura en el temporal del sistema: `iajedrez-gemini.png`.

## Mejoras de tablero, resumen y aprendizaje

El tablero define explícitamente ocho filas y ocho columnas iguales, incluso en finales sin piezas. Al abrir cualquiera de los estudios se solicita automáticamente Stockfish y se muestra la tabla prioritaria al terminar; los fallos conservan un acceso para reintentar. `static/study-ui.js` comparte la tabla entre ambos estudios: símbolos accesibles con etiqueta, ventaja perdida en peones de valoración y barras (tope visual de 5), comparación explícita de jugada real y alternativa.

Las pestañas son ahora Resumen de errores, Consejos, Cadena y Aprende. Aprende reúne recursos gratuitos verificados de Lichess, temas vinculados a jugadas concretas y acceso a la práctica existente con motor. Las antiguas referencias están dentro de un detalle desplegable. Los temas son una selección para las dos partidas precargadas, no extracción semántica general ni búsqueda automática de videos. Los enlaces de aperturas permiten explorar continuaciones y partidas; los de táctica ofrecen ejercicios y lecciones.

## Inicio y navegación de vistas

La ruta `/` muestra ahora el inicio de chat (`static/home.html`, `home.css`, `home.js`): historial con los dos estudios, bienvenida y campo PGN visual. Seleccionar un estudio muestra el prompt y PGN completos y un enlace al análisis `/?game=mauricio` o `/?game=entrevista`. `/prototype` sigue mostrando el tablero. No se importan nuevas partidas desde el inicio.

El encabezado de respuestas contiene cinco botones visibles, en orden: Resumen de errores, Consejos, Referencias, Cadena, Aprende. Se eliminó el desplegable Otras respuestas. Los nodos de jugadas negras tienen centro negro; los de blancas, blanco; la selección usa un aro azul exterior. El resto de la distribución se conserva. Referencias aportadas: `IAjedrez_inicio.png` y `IAjedrez_modulo_opciones.png`.

## Actualización vigente: segunda partida con motor (6 nov. 2026)

El usuario pidió incorporar la conversación Timmy-t–Kuanynsh al diseño aprobado y comprobarla con Stockfish. La página `/` carga ahora este estudio; `/?game=mauricio` conserva el anterior. Esta actualización prevalece sobre la descripción de la partida principal que sigue debajo. No se rediseñó la estructura ni se retiró `/demo`.

`interview.py` reutiliza las funciones de comparación de `review.py`, analiza las 54 decisiones blancas y comprueba explícitamente …Dh1+, …Cd5, Cc5 y Cg7+. `static/interview-ui.js` presenta las objeciones del usuario, síntesis atribuida y evidencia separadas. `static/review.js` selecciona el estudio mediante `?game=`; las API mantienen `mauricio` como valor predeterminado por compatibilidad y la interfaz envía explícitamente `entrevista`. No cambiar globalmente GAME_PATH para seleccionar partidas: deben coexistir de forma segura.

Stockfish 19 funciona en Windows en `engines/stockfish/stockfish-windows-x86-64-universal.exe`; detección: variable de entorno, PATH, carpeta local. No se distribuye el ejecutable. Hallazgo importante: 16.e4 permite …Txc3! seguido de …dxe4, omitido en ChatGPT; 21.Te2 coincide con la candidata principal en la ejecución observada. 29.Rf1 permite …Dh1+ y 45.Cc7 pierde el caballo. No codificar puntuaciones: se calculan en ejecución. Ver `GUION_ENTREVISTA_STOCKFISH.md` para cifras observadas, parámetros, atribución y límites.

Validación: 22 pruebas de servidor con motor real; `tests/ui_interview.py` verifica consultas conjuntas, variantes, práctica, retorno, JSON y escritorio/móvil con Edge. El script anterior `tests/ui_review.py` apunta ahora a `/?game=mauricio`. La conversación se archiva como síntesis en `static/conversacion-entrevista.md`, no como transcripción literal. PGN completo con relojes y encabezados aportados. Las consultas no persisten al recargar; la caché de motor no persiste al reiniciar el servidor.

Actualizado: 6 de noviembre de 2026. Leer este archivo primero. Es una síntesis operativa de la conversación, no una transcripción literal. No asumir acceso al historial del chat.

## Encargo y prioridad vigente

**Actualización Stockfish (6 de noviembre de 2026):** el usuario aportó una nueva partida de Chess.com, Mauricio0120–santoshglklklk (26 oct. 2026, 38 medias jugadas, 0–1 sin motivo), y una respuesta previa de ChatGPT sin motor. Solicitó validar con Stockfish y simular las mismas consultas en la interfaz. La página `/` usa ahora esa partida y `static/review.js`; conserva los estilos, componentes y tablero fijo del prototipo aprobado. `/demo` conserva la entrevista anterior. Ver `GUION_STOCKFISH.md` para el nuevo recorrido. Esta actualización prevalece sobre la descripción anterior de una demo principal sin motor.

Stockfish 16 ya está instalado en `/usr/games/stockfish` y accesible por PATH. El recorrido no usa Ollama: un tutor de plantillas reconoce las preguntas de la conversación y presenta evidencia calculada. No afirmar que comprende o valida cualquier pregunta. `review.py` compara mejor candidata y jugada real desde la misma posición, con profundidad objetivo 19 y límite de 1,5 s por búsqueda, Threads 1 / Hash 128 MB. Muestra profundidad real, perspectiva de blancas y etiquetas locales orientativas de 50/100/200 cp; los mates no se restan como centipeones. La caché es en memoria y se invalida con cambios de PGN, ejecutable o parámetros; las consultas del navegador se pierden al recargar.

Hallazgos que deben conservarse: 9.Cd2 no es el único error ni la primera caída relevante (también 7.Ag3). En esta revisión destacan 19.Tf3, 11.Th3 y 14.Rd2. La candidata citada 9.Df3 permite …Dc1+; mostrar esa respuesta junto a la hipótesis …Dxg3+ Dxg3. 19…Td2+ no es mate y la línea 20.Dxd2 Dxf3 21.gxf3 exd2 22.Rxd2 es legal, con cinco peones blancos y seis negros. Distinguir la respuesta calculada a 19.Tf3 de la jugada real …Td2+; sus evaluaciones son posiciones diferentes. Los valores exactos se calculan, no se codifican en la interfaz.

**Prioridad visual confirmada el 6 de noviembre de 2026:** el usuario exige el diseño exacto de `IAjedrez_prototipo_interactivo.html`. La ruta `/` sirve ese mismo archivo; `/prototype` es un acceso alternativo. No sustituirlo por una adaptación ni rediseñarlo. Posteriormente se editarán sus elementos conservando este diseño. La demo de la entrevista se mantiene en `/demo`, con sus datos e interacciones anteriores; aún no está integrada en el diseño exacto aprobado. Esta decisión prevalece sobre las descripciones anteriores de la demo como página principal.

El usuario, Mauricio, desarrolla un proyecto del curso universitario de Interacción Humano Computador. La entrega es una demostración de interfaz funcional para mañana, según lo indicado el 6 de noviembre de 2026. Verificar la fecha si se retoma más adelante.

El propósito es adaptar la interacción de un chat tradicional con IA para revisar partidas y aprender ajedrez. **No es prioritario construir una plataforma completa ni integrar una IA real para esta entrega.** El usuario autorizó partidas precargadas y funcionalidad acotada. Esta aclaración sustituye el plan inicial de priorizar Stockfish/Ollama.

## Evolución del encargo

1. El usuario aportó el prototipo HTML, dos PNG y un enlace a una conversación compartida que no pudo consultarse.
2. Luego pegó el contenido de esa conversación: interfaz de jugadas, tablero, panel de resultados y menú de otras vistas oculto por defecto.
3. Se preparó una base FastAPI + python-chess y adaptadores de Stockfish/Ollama. Las integraciones no se probaron con motor/modelo reales.
4. Se confirmó hardware: 32 GB RAM informados por el usuario; RTX 3050 con 6144 MiB VRAM comprobados con nvidia-smi. Se propuso Qwen3 4B en Ollama, sin instalarlo. No era una elección final medida.
5. El usuario aclaró el objetivo académico y plazo. Aportó una partida completa y una entrevista donde cuestionaba respuestas de ChatGPT.
6. Se consultaron tres PDF locales y se construyó una demo funcional basada en esa partida, sin depender de una IA en vivo.

## Desplazamiento de la interfaz

Por petición del usuario, el tablero permanece fijo en la ventana. Solo se desplazan la lista de Jugadas y variantes y el cuerpo de resultados (Consejos, Cadena, Referencias y Aprende); los encabezados y el formulario quedan fuera de esas áreas. En tablet los paneles dinámicos se apilan junto al tablero; en móvil se alternan con los botones Jugadas y variantes / Respuestas debajo del tablero fijo. Mantener esta estructura al editar contenido.

## Requisitos de interacción que deben conservarse

- Árbol/lista de jugadas a la izquierda, tablero central y un único panel de resultados a la derecha.
- «Otras respuestas» inicialmente oculto. Sus cuatro opciones: Consejos, Referencias, Cadena y Aprende; sustituyen contenido del mismo panel.
- Cadena significa dividir una tarea en pasos didácticos, con consultas por etapa; no mostrar razonamiento interno de un modelo.
- Tres recorridos: comprender un error; explorar una duda secundaria y regresar sin perder contexto; probar alternativas en el tablero.
- Priorizar síntesis, acceso rápido a jugadas, participación del usuario y exploración reversible.
- Las respuestas preparadas deben identificarse. No presentar texto editorial ni validación de legalidad como evaluación de Stockfish.

## Contexto de la partida y entrevista

Partida Timmy-t (1578, blancas) contra Kuanynsh (1594, negras), Lichess sTNRsqPl, 1 de noviembre de 2026, blitz 3+0. Resultado 0–1 por tiempo. La perspectiva de la entrevista corresponde a blancas. El archivo `static/partida-entrevista.pgn` conserva las 108 medias jugadas y sus relojes; contiene los metadatos relevantes, no todos los encabezados originales.

Momentos principales aportados por el usuario:

- **16.e4:** el usuario cuestionó una valoración demasiado positiva porque activa el alfil negro de b7. Mostrar el cambio de diagonal y el peón aislado de d4, sin declarar una evaluación de motor.
- **21.Te2:** el usuario explicó que intentaba activar su torre por e2–c2–c6. Reconocer esa intención; separar el plan del consumo del reloj. No etiquetar como error por gastar tiempo.
- **29.Rf1 (Kf1 en PGN):** el usuario detectó …Dh1+. Se verificó la legalidad de …Dh1+ Re2 Dxh3. Es una línea ilustrativa: no se demostró que Re2 sea forzada ni que la pérdida del peón sea inevitable contra cualquier respuesta.
- **45.Cc7:** permite …Cxc7, ocurrido en la partida. Ejercicio desde antes de la jugada: Cc5 y Cg7+ son alternativas legales que evitan esa captura inmediata; no se anuncian como mejores movimientos de motor.
- Final: derrota por tiempo, no jaque mate. Los relojes son registros después de cada jugada, no un reloj en vivo ni el instante exacto de caída de bandera.

La larga respuesta de ChatGPT pegada por el usuario tenía valoraciones que luego fueron corregidas. No tratarla como una fuente ajedrecística validada ni copiar sus afirmaciones absolutas. Tampoco inferir pensamientos o causas psicológicas no confirmadas.

## Archivos y rutas actuales

| Archivo/ruta | Función |
| --- | --- |
| `app.py` | Servidor FastAPI; validación de jugadas y API del laboratorio |
| `/` → `IAjedrez_prototipo_interactivo.html` | Diseño exacto aprobado para mostrar el proyecto |
| `/demo` → `static/demo.html` | Demo de la entrevista conservada |
| `static/demo.js` | Estados, consultas, retorno al paso, variantes, ejercicio |
| `static/demo-data.js` | Ocho momentos y respuestas editoriales preparadas |
| `static/demo.css`, `static/style.css` | Estilos; se conserva la organización visual del prototipo |
| `/api/demo` | Lee el PGN y devuelve movimientos, SAN, relojes y encabezados |
| `/api/position` | Valida secuencia desde posición inicial mediante python-chess |
| `/lab` → `static/index.html`, `static/app.js` | Laboratorio anterior: importación, estudio JSON, adaptadores de motor y tutor |
| `/prototype` | Mismo HTML aprobado, conectado al recorrido Stockfish |
| `review.py`, `/api/review/*` | Partida, análisis de blancas, consultas y comparación de candidatas |
| `static/review.js` | Navegación, consultas, variantes y práctica del recorrido principal |
| `static/partida-mauricio.pgn`, `static/conversacion-mauricio.md` | Partida nueva y síntesis atribuida de la conversación |
| `tests/test_review.py`, `tests/ui_review.py` | Regresiones de motor/API y simulación de navegación |
| `INICIAR_DEMO.cmd` | Inicia servidor local en 127.0.0.1:8765 |
| `tests/test_app.py` | Siete pruebas de API |
| `tests/ui_demo.py` | Tres recorridos en Edge con Playwright; requiere servidor activo |

El laboratorio guarda/restaura estudios JSON, pero **la demo principal no persiste consultas al recargar**. No confundir ambas funcionalidades. Las consultas de la demo son respuestas preparadas por tema; fuera de los temas previstos aparece un aviso explícito. No existe conversación generativa ni memoria de un LLM en esta demo.

## Documentación disponible

- `README.md`: ejecución y descripción general; contiene además el alcance previo del laboratorio.
- `ALCANCE_Y_CONTEXTO.md`: alcance y decisiones. Su sección inicial de cambio de prioridad prevalece sobre la propuesta anterior que aparece debajo.
- `GUION_DEMOSTRACION.md`: pasos exactos para exponer, límites y comprobaciones.
- `INVESTIGACION_A_INTERFAZ.md`: trazabilidad de hallazgos a decisiones, con páginas de los PDF.

Material de investigación revisado:

- `Needfinding-CornejoMauricio.pdf`: texto extraído, 20 páginas. Usuario casual intermedio; necesita tablero, resumen, acceso rápido, verificación, explicaciones y práctica.
- `IHC-CornejoMauricio-U2paper.pdf`: texto extraído, cuatro páginas. Priorizar información y estructurar interacción; inspirado en PAIL/Beyond Code Generation.
- `IHC-BeyondPaper-Apuntes-CornejoMauricio.pdf`: página manuscrita renderizada y vista como imagen; bosquejos y relaciones, no transcripción literal.

La conversación inicial también citó Interactive Reasoning (Pang et al., 2026), PromptChainer (Wu et al., 2022), Beyond Code Generation (Zamfirescu-Pereira et al., 2025) y From Conversation to Human-AI Common Ground (Chen et al., 2026). No se verificaron aquí sus textos completos ni todos los datos bibliográficos. Evitar afirmar una revisión académica exhaustiva.

## Ejecución y verificación

Recorrido Stockfish verificado: 17 pruebas de servidor pasan, incluidas comparaciones reales, variantes legales, interpretación acotada, rechazo de PGN distinto y motor ausente. `tests/ui_review.py` reproduce la pregunta con PGN, 9.Cd2, 9.Df3, defensa del final, práctica evaluada por el motor y retorno al paso exacto; sin errores de consola. Se comprobó tablero fijo y scroll independiente a 1440×900, 1366×768, 900×900 y 390×844. La ruta de fallo 503 conserva la pregunta y permite reintentar sin inventar respuestas. Capturas en `/tmp/iajedrez-stockfish-*.png`.

Verificación del desplazamiento (Linux, 6 de noviembre de 2026): Playwright 1.64.1 y Chromium Headless Shell instalados en `venv` y la caché del usuario. Se comprobó `/` a 1440×900, 1366×768, 900×900 y 390×844: lista de jugadas y cuerpo de las cuatro vistas con desplazamiento independiente, coordenadas del tablero constantes, práctica d3→d4 y retorno, menú inicialmente oculto y consola sin errores. Se revisaron capturas de escritorio y móvil; scripts y capturas de esta comprobación están en `/tmp`, no forman parte del repositorio. En Linux se ejecuta con `venv/bin/python`; los comandos Windows siguientes corresponden al entorno anterior.

Entorno Windows/PowerShell; Python 3.13 y Node 22 observados. `.venv` contiene dependencias instaladas. Puede no existir en otro equipo. `requirements.txt` y `requirements-dev.txt` son las fuentes de instalación. Para extraer/ver PDF se instalaron además pypdf y pymupdf en el entorno, sin añadirlos como dependencias de la aplicación.

```powershell
.venv/Scripts/python -m uvicorn app:app --host 127.0.0.1 --port 8765
.venv/Scripts/python -m pytest -q
.venv/Scripts/python tests/ui_demo.py
node --check static/demo.js
```

El puerto 8000 dio WinError 10013 incluso al reintentar con permisos; 8765 funcionó. No asumir que el servidor iniciado durante el chat siga vivo. Si hay uno activo, verificar antes de lanzar otro. No detener procesos ajenos.

Última validación: siete pruebas de API pasaron; recorrido UI pasó en Edge a 1440×1000 y 390×844, sin errores de consola, incluyendo retorno al paso exacto, variantes, ejercicio, consulta fuera de guion, reinicio y resultado por tiempo. Browser plugin no estaba disponible; se usó Playwright con Edge instalado. Capturas en la carpeta temporal de Windows: `iajedrez-demo-desktop.png`, `iajedrez-demo-chain.png`, `iajedrez-demo-mobile.png`. Una advertencia de deprecación de Starlette/httpx apareció en tests; no fue un fallo.

No confundir estas comprobaciones con evaluación de usabilidad con participantes ni con pruebas de Stockfish/Ollama.

## Pendientes y cómo retomar

1. Si el usuario pide cambios para la exposición, priorizar el nuevo recorrido Stockfish y `GUION_STOCKFISH.md`. No reinstalar modelos ni rediseñar desde cero por iniciativa propia.
2. Probar cambios de la interfaz principal con `tests/ui_review.py` (`tests/ui_demo.py` corresponde a `/demo`); verificar que se conserva jugada, paso y consulta al regresar.
3. Si se retoma el producto después de la entrega: instalar/verificar motor y modelo, análisis completo de errores, persistencia y preguntas generativas son trabajo futuro.
4. No quedan preguntas de contexto que bloqueen la demo. Confirmar solo requisitos nuevos o cambios de fecha/entrega.

Preferencias del usuario: avanzar con lo disponible; preguntar si falta contexto; mantener documentación `.md` suficiente para otros agentes. No necesita que todo esté al 100% para demostrar la propuesta.

## Estado del repositorio y cautelas

El diseño aprobado y el desplazamiento se guardaron en el commit `1b12f7e`, solicitado por el usuario. Los cambios del nuevo recorrido Stockfish están pendientes de commit. Revisar `git status` antes de modificar; no incluir el entorno local `venv/` ni borrar materiales aportados por el usuario. Los PNG de referencia se conservan.

Este documento no reemplaza el código: verificar estado real antes de prometer una funcionalidad. La conversación literal no está archivada en su totalidad; los requisitos, decisiones y hallazgos relevantes sí están resumidos entre estos documentos y los datos de la demo.
