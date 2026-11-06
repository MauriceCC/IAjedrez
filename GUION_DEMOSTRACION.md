# Demostración IHC · IAjedrez

Este guion corresponde a la demo de la entrevista en `/demo`. La página principal muestra el prototipo con el diseño exacto aprobado y sus ejemplos originales.

## Objetivo de la propuesta

Mostrar cómo adaptar la interacción de un chat con IA a la revisión de partidas: el usuario localiza una decisión, ve su posición, cuestiona una explicación y prueba una alternativa sin reconstruir el contexto en otra pestaña.

Esta entrega es una **demostración funcional con contenido preparado**, no una evaluación del rendimiento de un modelo de IA. La partida real es Timmy-t–Kuanynsh, 1 de noviembre de 2026. La interfaz revisa las blancas, según la perspectiva de la entrevista.

## Preparación

1. Abre `INICIAR_DEMO.cmd` y deja la ventana abierta. Si ya hay un servidor en 8765, usa ese servidor; no hace falta iniciar otro.
2. Abre http://127.0.0.1:8765/demo en Edge o Chrome.
3. Pulsa «Reiniciar recorrido» para comenzar sin consultas anteriores.
4. Verifica que aparece 29.Rf1 y que «Otras respuestas» está cerrado.

La aplicación necesita el servidor Python local. No requiere Internet para los recorridos, Stockfish ni Ollama. Solo los enlaces de Referencias requieren Internet. No abras `demo.html` directamente con doble clic: usa la dirección local.

## Presentación inicial · 30 segundos

“En la entrevista, el jugador tuvo que cambiar de pestaña para ver el tablero y buscar jugadas entre respuestas largas. Nuestra propuesta reúne el tablero, las decisiones de la partida y las consultas contextualizadas. El resumen distingue errores demostrables de planes que necesitan discusión.”

La notación está en español: R = rey, D = dama, T = torre, A = alfil y C = caballo. El PGN original conserva la notación inglesa.

## Recorrido 1 · Comprender un error · 1 minuto

1. En la tabla, pulsa **45.Cc7**. También puedes seleccionar ese momento en la lista y abrir Otras respuestas → Cadena.
2. Expande “Identificar qué cambia”. El tablero sitúa el caballo blanco en c7 y el negro en d5.
3. Explica que el jugador escapaba del rey de f5, pero eligió una casilla atacada por el caballo negro.
4. Pulsa “Ver …Cxc7”. Observa la captura. Pulsa “Volver a la partida”.

**Qué demuestra:** acceso directo al momento, conexión entre explicación y tablero, descomposición en pasos.

## Recorrido 2 · Resolver una duda y regresar · 1–2 minutos

1. Selecciona **29.Rf1** y abre Cadena si no está visible.
2. Abre el paso 3, “Comparar consecuencias”.
3. Pulsa la pregunta sugerida **“¿La dama puede ir a h1 y ganar un peón?”**.
4. Observa que la pregunta aparece bajo la jugada a la izquierda.
5. Pulsa “Ver la variante en el tablero”. Usa la flecha derecha dos veces: …Dh1+ → Re2 → …Dxh3.
6. Pulsa **“Volver al análisis original”** dentro de la respuesta.
7. Comprueba que regresaste a 29.Rf1, al paso 3 y que la consulta sigue conservada. Puedes reabrirla desde el árbol.

**Qué demuestra:** una duda no obliga a abandonar la tarea principal ni perder el contexto. La variante es legal e ilustrativa; no afirmamos que Re2 sea forzada o que sea la mejor línea de motor.

## Recorrido 3 · Aprender probando · 1 minuto

1. Abre Otras respuestas → **Aprende**.
2. La posición retrocede a antes de 45.Cc7. Selecciona **e6**, luego **c7**.
3. Pulsa “Ver respuesta …Cxc7” y observa por qué falla.
4. Pulsa “Reintentar”. Selecciona **e6**, luego **c5**; observa la explicación.
5. Opcional: reintenta y prueba **e6 → g7**, que da jaque.
6. Pulsa “Volver al análisis original”.

**Qué demuestra:** el usuario piensa antes de ver la respuesta, puede equivocarse y repetir sin alterar la partida. Los destinos legales se resaltan; un destino ilegal se rechaza.

## Dos ejemplos adicionales de la entrevista

- **16.e4:** pulsa la pregunta del alfil de b7. Recorre los intercambios. La respuesta reconoce el coste estructural y no equipara “ruptura central” con “buena jugada”.
- **21.Te2:** pregunta “Mi intención era mejorar la torre y hacerla activa”. La respuesta reconoce el plan Te4–e2–c2–c6 y separa esa intención del tiempo consumido. Recorre la maniobra con las flechas.

## Cierre · 30 segundos

“El aporte que estamos evaluando es la organización de la interacción: síntesis, acceso a la posición, preguntas vinculadas y exploración reversible. El siguiente paso sería probar estos recorridos con usuarios y medir si encuentran el error, conservan el contexto y comprenden la alternativa.”

## Límites que conviene explicar

- Textos y preguntas preparados para la partida de la entrevista; una consulta fuera de los temas previstos muestra un aviso explícito.
- Las consultas duran durante la sesión de la página. Recargar o reiniciar borra el recorrido de esta demo.
- Legalidad comprobada mediante python-chess; las valoraciones estratégicas no están verificadas por Stockfish.
- No hay puntuaciones inventadas ni clasificación automática de toda la partida.
- El resultado final es derrota por tiempo, no jaque mate. Los relojes son registros del PGN, no relojes en vivo.
- `/lab` conserva las herramientas experimentales de importación, Stockfish y Ollama; no forman parte del recorrido necesario para la exposición.

## Comprobación realizada

Siete pruebas de API aprobadas. Prueba de interfaz en Edge con Playwright a 1440×1000 y 390×844: los tres recorridos, retorno al paso exacto, variante legal, respuesta fuera de guion, menú, reinicio, estado de resultado y consola sin errores. Plugin Browser no disponible; se utilizó Playwright directamente.

Para repetir (con el servidor ejecutándose):

```powershell
.venv/Scripts/python -m pytest -q
.venv/Scripts/python tests/ui_demo.py
```

Las capturas se guardan en la carpeta temporal de Windows, con nombres `iajedrez-demo-desktop.png`, `iajedrez-demo-chain.png` e `iajedrez-demo-mobile.png`.
