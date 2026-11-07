# Timmy-t–Kuanynsh: conversación contrastada con Stockfish

## Abrir y demostrar

1. Ejecuta `INICIAR_DEMO.cmd` y abre http://127.0.0.1:8765. La página principal conserva el diseño aprobado y carga Timmy-t–Kuanynsh, 54 jugadas, 3+0, 0–1 por tiempo.
2. Pulsa **Analizar mi partida**. Se calculan las 54 decisiones blancas; la primera consulta puede tardar unos minutos. La caché vive en el servidor y no sobrevive a su reinicio. Si el motor falla se muestra un error, nunca una evaluación inventada.
3. El resumen responde por etapas, desde la apertura hasta el final, y ofrece variantes del momento de mayor caída de cada etapa. **Ver resumen de errores** ordena las jugadas por caída estimada. **Consejos** muestra las 54 decisiones en orden cronológico.
4. Consulta `En la jugada 16 activo el alfil de b7; en la 21 quería activar mi torre; en la 29 la dama puede entrar por h1`. La respuesta conserva las tres objeciones, distingue la conversación de la revisión didáctica y añade la evidencia calculada.
5. Abre `¿29.Kf1 permite Qh1+?`. Compara la línea citada con la defensa calculada por Stockfish. Recorre las variantes con las flechas y vuelve a la misma consulta.
6. Consulta `¿Qué ocurrió en 45.Nc7?`. En **Otras respuestas → Aprende**, mueve el caballo de e6 a g7 o c5; el motor evalúa la candidata. Puedes reintentar y volver sin alterar la partida.
7. En **Referencias** se conserva la síntesis atribuida y se puede descargar el PGN con todos los encabezados aportados y relojes. En el resumen se descarga la evidencia JSON de la sesión (versión, fecha UTC, hash del PGN, parámetros, profundidad real, variantes y puntuaciones).

El estudio previo sigue en `/?game=mauricio`; la demo preparada, en `/demo`; el laboratorio, en `/lab`. Hay enlaces entre ambos estudios. El navegador conserva las consultas solo hasta recargar. El tutor usa plantillas acotadas, no un LLM.

## Comprobación real realizada el 6 de noviembre de 2026

Motor: **Stockfish 19**, ejecutable local `engines/stockfish/stockfish-windows-x86-64-universal.exe`. El servidor busca primero `STOCKFISH_PATH`, después PATH y finalmente los ejecutables locales `engines/stockfish*.exe` (también en subcarpetas). `engines/` está excluido de Git. Los binarios proceden de la [distribución oficial](https://github.com/official-stockfish/Stockfish/releases/tag/sf_19).

Método: una búsqueda libre y, cuando es necesario, una búsqueda restringida a la jugada real desde la misma posición. Objetivo profundidad 19, límite 1,5 segundos por búsqueda, Threads 1, Hash 128 MB. Perspectiva de blancas. Las etiquetas locales usan 50/100/200 centipeones; los mates se tratan por separado. Los valores siguientes son una ejecución observada, no constantes del programa ni un análisis exhaustivo. Pueden variar entre búsquedas.

| Decisión | Candidata / evaluación | Jugada real / evaluación | Hallazgo |
| --- | --- | --- | --- |
| 16.e4 | Te2, +0,13 | e4, −4,55 | La respuesta calculada empieza por …Txc3!, recurso omitido en la conversación. |
| 21.Te2 | Te2, −0,07 | Te2, −0,07 | Coincide con la primera candidata de esta búsqueda; no se etiqueta como error por consumir tiempo. |
| 29.Rf1 | Cc6, +0,17 | Rf1, −0,56 | La variante del motor incluye …Dh1+ Re2 Dxh3; Re2 sigue siendo una elección, no la única jugada legal. |
| 45.Cc7 | Cg7+, +2,94 | Cc7, −5,82 | …Cxc7 pierde el caballo; ambas alternativas citadas se evalúan separadamente. |

Las evaluaciones de esta tabla alcanzaron profundidad 19. Una comprobación adicional desde después de 29.Rf1 dio −0,68 al forzar …Dh1+ y +0,08 al forzar la respuesta real …Cd5, ambas a profundidad 19. Son búsquedas distintas, de ahí que no coincidan exactamente con el valor calculado desde antes de Rf1.

**Corrección central:** tras 16.e4 Txc3 17.Dxc3 dxe4, el peón negro ataca simultáneamente al alfil de d3 y al caballo de f3. En la partida las negras jugaron directamente …dxe4. No basta con evaluar los intercambios ocurridos para declarar buena la ruptura. La interfaz muestra la continuación calculada, no una variante inventada.

## Validación

```powershell
.venv/Scripts/python -m pytest -q -p no:cacheprovider
node --check static/review.js
node --check static/interview-ui.js
.venv/Scripts/python tests/ui_interview.py
```

22 pruebas de servidor pasaron, incluidas búsquedas reales, legalidad de todas las variantes, partida seleccionada, consultas conjuntas, PGN incorrecto y motor ausente. Playwright con Edge (Browser plugin no disponible) verificó 1440×900 y 390×844: tablero, metadatos, consultas, variantes, práctica, retorno, evidencia descargada, desplazamiento y estudio anterior, sin errores de consola. Capturas y JSON de prueba en el directorio temporal del sistema (`iajedrez-interview-*`). No se probaron otros navegadores ni usabilidad con participantes.
