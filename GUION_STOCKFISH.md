# Demostración con Stockfish · partida de Mauricio

## Preparación

1. Inicia el servidor como indica README.md y abre http://127.0.0.1:8765.
2. La partida Mauricio0120–santoshglklklk ya está cargada. Confirma que «Otras respuestas» empieza cerrado y que el tablero permanece fijo mientras desplazas los otros módulos.
3. Escribe: «Hola ChatGPT, eres experto en ajedrez, ¿podrías indicarme cuál fue mi error en esta partida, por favor?». Puedes adjuntar el mismo PGN de `static/partida-mauricio.pgn`; no hace falta volver a pegarlo. La interfaz no acepta otra partida en este recorrido.
4. Envía. El primer análisis puede tardar alrededor de un minuto. El aviso de trabajo no contiene evaluaciones inventadas; si Stockfish falta o falla aparece un error y se conserva tu pregunta para reintentar.

## 1. Revisar la respuesta inicial

La respuesta utiliza las 19 comparaciones de blancas. Abre «Ver resumen de errores» para localizar las caídas de evaluación más grandes. La revisión comprobada destaca 19.Tf3, 11.Th3 y 14.Rd2; los números pueden variar con la búsqueda y versión del motor. Las etiquetas son orientativas de IAjedrez, no oficiales de Chess.com.

Muestra que 7.Ag3 también merece revisión antes de afirmar que 9.Cd2 fue el primer error importante. Las candidatas, las evaluaciones y las variantes vienen del motor; los textos explicativos usan plantillas.

## 2. Cuestionar 9.Cd2 y regresar

1. Selecciona 9.Cd2 en la tabla. En Cadena abre el paso 3.
2. Pregunta «¿Fue 9. Nd2 el primer error importante?».
3. Abre «Respuesta a la jugada de la partida». Recorre con las flechas 9.Cd2, …Dxg3+ y 10.Re2.
4. Pulsa «Volver al análisis» y después «Volver al análisis original».
5. Debes volver a 9.Cd2 y al paso 3. La pregunta permanece bajo esa jugada en el árbol y se puede reabrir.

La legalidad confirma que Re2 era la única respuesta al jaque. Eso no basta para concluir que esta fue la mayor caída de toda la partida.

## 3. Contrastar 9.Df3, propuesta por ChatGPT

1. En Referencias pulsa «Comprobar Df3», o escribe «¿Era mejor 9. Qf3?».
2. Compara la línea hipotética Df3 Dxg3+ Dxg3 con «Respuesta calculada a 9.Df3».
3. En la respuesta calculada aparece …Dc1+, una opción que la explicación anterior no contemplaba. No obligues a las negras a capturar en g3.
4. Regresa al análisis y abre Aprende desde 9.Cd2. Selecciona d1 y f3: la propuesta se valida y analiza de nuevo con Stockfish.
5. Pulsa «Ver respuesta del motor». Luego reintenta con g1 → e2, o usa «Ver pista» para consultar la candidata de la revisión.
6. «Volver al análisis original» restaura la posición y el paso anterior.

## 4. Explorar el final sin confundir derrota con mate

1. Pregunta «¿Era mate después de 19...Rd2+?».
2. La respuesta confirma cuatro movimientos legales y muestra el 0–1 sin inventar el motivo.
3. Abre «Variante citada…» y avanza: 20.Dxd2 Dxf3 21.gxf3 exd2 22.Rxd2.
4. Quedan torre y alfil contra torre y caballo, con cinco peones blancos y seis negros. La variante conserva la partida original intacta.
5. Contrasta esa línea con la continuación principal calculada. No declares una variante forzada por el mero hecho de que es legal.

19.Tf3 se evalúa antes de conocer qué responderá el rival. En la partida las negras eligieron …Td2+, que permite Dxd2. La evaluación después de ese jaque puede ser mejor para blancas que la obtenida al considerar la respuesta más fuerte a Tf3: no son la misma posición.

## Límites y comprobación

- Stockfish está limitado a profundidad objetivo 19 o 1,5 s por búsqueda. Se muestra la profundidad realmente alcanzada; las cifras son aproximadas.
- Los comentarios son de un tutor de plantillas, no un LLM. Una pregunta no reconocida se indica como no validada; prueba «Quiero comprar un telescopio» para verificarlo.
- Las consultas se conservan durante la sesión de la página; recargar o reiniciar las borra. El análisis se reutiliza en memoria del servidor.
- El recorrido funciona localmente sin Ollama ni acceso a Internet, una vez instalado Stockfish. Los enlaces externos sí requieren conexión.
- Ejecuta `venv/bin/python tests/ui_review.py` con el servidor activo para reproducir esta navegación mediante Playwright y Stockfish real. Las capturas van al directorio temporal del sistema.
