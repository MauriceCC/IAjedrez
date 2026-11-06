# De la investigación a la interfaz

Material revisado: texto extraído de `Needfinding-CornejoMauricio.pdf` y `IHC-CornejoMauricio-U2paper.pdf`, imagen renderizada de la página de apuntes `IHC-BeyondPaper-Apuntes-CornejoMauricio.pdf`, prototipo y conversación de la entrevista suministrada en el chat.

La lectura de los apuntes manuscritos sirve para reconocer el bosquejo y sus relaciones; no se utiliza como transcripción literal. Los artículos originales completos no se revisaron para esta iteración.

| Evidencia local | Necesidad | Respuesta en la demo | Cómo observarla |
| --- | --- | --- | --- |
| Needfinding p. 6 y p. 10: el usuario cambia a Lichess para visualizar | Ver tablero sin cambiar de contexto | Tablero integrado y sincronizado | Seleccionar 29.Rf1 y ver su posición |
| Needfinding pp. 11–12: tabla y acceso rápido a la jugada | Localizar lo relevante | Tabla de momentos con enlaces y filtro de jugadas | Ir a 45.Cc7 con un clic |
| Needfinding p. 14; U2paper pp. 3–4: priorizar y no distraer | Reducir búsqueda y saturación | Resumen primero; otras vistas en menú inicialmente oculto | Abrir Consejos y actualizar el mismo panel |
| Needfinding p. 7 y pp. 19–20: el jugador señala una omisión | Permitir cuestionar y corregir una explicación | Duda secundaria por jugada, respuesta y regreso al paso original | Preguntar por …Dh1+ y regresar |
| Entrevista: intención de 21.Te2 | Incorporar el propósito del jugador | Explicación preparada reconoce la maniobra y separa reloj de calidad | Enviar la pregunta sobre activar la torre |
| Entrevista: duda sobre 16.e4 | Explorar consecuencias sin etiquetas absolutas | Secuencia de cambios y explicación con matices | Seguir los intercambios y observar el alfil |
| Needfinding pp. 15 y 17: guía sin resolver todo; práctica | Aprender con participación | Ejercicio de destinos del caballo, pista a demanda, reintento | Comparar Cc7 y Cc5 |
| Needfinding p. 16: materiales para estudiar | Continuar fuera de la revisión | Referencias generales seleccionadas manualmente | Abrir Referencias |
| Needfinding pp. 9, 13 y 20: motor para verificar | Diferenciar evidencia y explicación | Legalidad comprobada; procedencia editorial visible | No confundir comentarios preparados con evaluación Stockfish |

## Decisiones de IHC

- **Proximidad y región común:** consultas bajo su jugada y respuesta dentro del panel principal.
- **Continuidad:** lista conectada de jugadas y pasos secuenciales de la Cadena.
- **Consistencia:** misma selección y contexto al cambiar entre vistas.
- **Visibilidad de estado:** jugada seleccionada, turno, variante, consulta guardada y destino legal.
- **Control del usuario:** reintentar, volver a la partida y volver al análisis original.
- **Reconocimiento:** preguntas sugeridas y acceso directo a los momentos, sin memorizar números de jugada.
- **Divulgación progresiva:** etapas desplegables y menú de vistas cerrado por defecto.
- **Prevención de errores:** movimientos ilegales rechazados y variante separada de la partida.

Son intenciones de diseño implementadas, no pruebas de que la interfaz ya sea usable para todos. Falta evaluación con usuarios.

## Ajustes de contenido respecto al chat original

- No declarar que 21.Te2 fue un error solo por el tiempo consumido.
- No etiquetar 16.e4 como inequívocamente buena: mostrar la activación del alfil y la estructura resultante.
- La secuencia 29…Dh1+ 30.Re2 Dxh3 es legal, pero una línea posible no prueba que la ganancia sea forzada contra cualquier respuesta.
- 45.Cc7 permite la captura real …Cxc7. Las alternativas del ejercicio son legales; no se presentan como mejores jugadas de motor.
- El resultado oficial es por tiempo, aunque hubo pérdida material. Evitar equipararlo a mate.
- No atribuir pensamientos o causas psicológicas al jugador que la entrevista no confirme; la presión del reloj es observable, su efecto causal no está demostrado.

## Mini evaluación propuesta para después de la exposición

Pedir a una persona de nivel intermedio que complete los tres recorridos sin indicarle qué botón pulsar. Registrar: éxito al encontrar la jugada, pérdida o conservación del contexto al regresar, errores de interacción y explicación verbal de por qué Cc7 pierde el caballo. No inventar resultados ni presentar la prueba automatizada como evaluación de usabilidad.
