# IAjedrez: alcance, estado y contexto pendiente

Actualizado: 6 de noviembre de 2026. Documento de seguimiento: diferencia lo implementado de lo propuesto y de lo comprobado.

## Cambio de prioridad confirmado para la entrega IHC

El usuario aclaró que la entrega de mañana consiste en demostrar una interfaz funcional, no en completar una aplicación con IA. Se priorizaron los tres recorridos con la partida real suministrada y respuestas preparadas. Esta sección sustituye el orden de trabajo anterior que priorizaba instalar modelos.

**Ya implementado en la demo principal:** partida completa (108 medias jugadas), relojes del PGN, ocho momentos desde apertura a final, tablas, Cadena con explicaciones, preguntas asociadas a jugada/paso, duda secundaria con retorno al contexto exacto, variantes reproducibles y Aprende con pista/reintento. Los movimientos se validan; los comentarios son editoriales y están identificados como preparados.

**Investigación revisada:** los tres PDF locales ya están disponibles y fueron consultados (texto de Needfinding y U2paper, imagen de los apuntes). El público identificado es un jugador casual de nivel intermedio. [Trazabilidad](INVESTIGACION_A_INTERFAZ.md).

**Documentación de entrega:** [Guion de demostración](GUION_DEMOSTRACION.md). Inicio con `INICIAR_DEMO.cmd` y http://127.0.0.1:8765. La demo no requiere un modelo ni motor instalados. Las integraciones previas permanecen en `/lab`.

**Validación de esta iteración:** siete pruebas de API y tres recorridos de interfaz aprobados en Edge, escritorio y móvil. Stockfish/Ollama siguen sin prueba real; no se atribuyen sus evaluaciones al contenido preparado. No hay dudas de contexto que bloqueen esta demostración. El análisis completo automático, modelos locales y despliegue quedan para una iteración posterior.

Las secciones que siguen registran la base técnica y la propuesta anterior; los pendientes marcados allí se refieren principalmente al laboratorio general, no a los recorridos preparados de la demo.

## Objetivo

Convertir el prototipo en una herramienta educativa de análisis de ajedrez en español. Los tres recorridos prioritarios son comprender un error, explorar una duda secundaria y regresar al análisis, y probar alternativas en el tablero.

Se conserva la organización de jugadas, tablero y panel único de resultados. «Otras respuestas» comienza oculto y permite cambiar a Consejos, Referencias, Cadena o Aprende. La Cadena organiza tareas didácticas y conclusiones verificables; no representa el razonamiento interno del modelo.

## Estado real de la implementación

| Área | Incluido actualmente | Pendiente |
| --- | --- | --- |
| Referencia visual | HTML y PNG originales conservados; estilos reutilizados en la aplicación | Afinar fidelidad visual y accesibilidad |
| Partidas | Ejemplo, importación de línea principal PGN, navegación | PGN con posiciones iniciales personalizadas y variantes |
| Tablero | Validación mediante python-chess, promoción elegible, final de partida | Mejoras de interacción y notación visible |
| Aprende | Variante activa con movimientos legales y regreso a la posición original | Ejercicios adaptativos y varias ramas persistentes |
| Stockfish | Adaptador UCI y análisis por posición con hasta tres variantes | Instalar/configurar motor y comprobarlo de extremo a extremo |
| Errores | El prototipo contiene ejemplos simulados; la aplicación real analiza posiciones | Tabla real de errores de toda la partida, progreso y cancelación |
| Tutor | Adaptador Ollama con posición y evidencia del motor | Instalar modelo y evaluar calidad, latencia y fidelidad al motor |
| Cadena | Cuatro etapas y consultas asociadas a posición/etapa | Conclusiones por etapa y árbol de preguntas con historial |
| Consejos y referencias | Orientaciones y enlaces generales | Tablas contextualizadas y catálogo por concepto verificado |
| Persistencia | Exportación/importación JSON de partida, variante activa y consultas | Guardado automático, múltiples estudios y base de datos |

El tutor recibe cada pregunta de forma independiente: conservar preguntas en la interfaz todavía no equivale a proporcionarle memoria conversacional. Las instrucciones del modelo reducen errores, pero no garantizan que todas sus afirmaciones sean correctas.

## Equipo y modelo local propuesto

- RAM: 32 GB, informada por el usuario.
- GPU: NVIDIA GeForce RTX 3050 con **6144 MiB (6 GiB) de VRAM**, comprobados mediante `nvidia-smi`.
- Sistema de trabajo: Windows y PowerShell.
- Ollama no se encontró en el PATH al realizar esta comprobación; eso no descarta una instalación fuera del PATH.

Propongo empezar con **Qwen3 4B en Ollama (`qwen3:4b`)** como línea base de evaluación. El catálogo oficial ofrece la cuantización Q4_K_M con unos 2,5 GB de descarga y licencia Apache 2.0. Es una propuesta conservadora para dejar espacio de GPU al contexto y al sistema; el tamaño del archivo no equivale a la VRAM total durante la inferencia.

Qwen3 8B queda como alternativa para comparar calidad: su paquete Q4_K_M ocupa unos 5,2 GB, por lo que el margen en esta GPU será menor. Puede requerir descargar parte del cálculo a RAM/CPU. No se promete una velocidad concreta sin medirla en este equipo. Los 32 GB de RAM ayudan, pero no sustituyen la velocidad de la VRAM.

Stockfish calculará variantes y evaluaciones; el modelo redactará explicaciones educativas. No se propone entrenar un modelo desde cero ni usar el modelo de lenguaje para decidir la legalidad.

### Configuración prevista

Después de instalar Ollama, en PowerShell:

```powershell
ollama pull qwen3:4b
$env:OLLAMA_MODEL = 'qwen3:4b'
$env:STOCKFISH_PATH = 'C:\ruta\stockfish.exe'
.venv/Scripts/python -m uvicorn app:app --host 127.0.0.1 --port 8765
```

El servicio Ollama debe estar ejecutándose. Estas variables se aplican a la terminal actual; reiniciar el servidor después de cambiarlas. Los comandos son instrucciones para la instalación pendiente, no una afirmación de que ya se ejecutaron.

Para el siguiente ajuste de integración se propone probar un contexto inicial de 4096 tokens y desactivar el modo thinking de Qwen3 mediante la API. Estos parámetros todavía no están configurados explícitamente en `app.py`. Hay que comprobar que el límite de generación produzca una respuesta completa antes de adoptar el modelo como configuración final.

## Validación disponible y criterios siguientes

En la sesión anterior pasaron cinco pruebas de API: movimientos legales/ilegales, enroque, PGN, jaque mate y motor ausente. Se comprobó en Edge con Playwright el menú oculto, carga del ejemplo, captura legal en una variante, regreso y anchura móvil. Se corrigió un desbordamiento. Es evidencia acotada, no una auditoría completa de usabilidad o accesibilidad.

Todavía no se ha validado aquí la ejecución de Stockfish ni del modelo local. El siguiente hito debería comprobar:

1. Motor real: variantes legales, perspectiva de evaluación y estados de mate/tablas.
2. Tutor: respuesta no vacía, español comprensible, separación entre evidencia e hipótesis, errores de conexión recuperables.
3. Rendimiento: tiempo de respuesta en frío y en caliente, uso de GPU con `ollama ps` y VRAM con `nvidia-smi`.
4. Calidad: preguntas de un conjunto fijo de posiciones, verificadas contra el motor y revisadas por una persona que conozca ajedrez.

## Orden propuesto de trabajo

1. Instalar y verificar Stockfish + Ollama + Qwen3 4B.
2. Implementar el resumen real de errores con comparación antes/después y pruebas de perspectiva de ambos colores.
3. Completar la Cadena, dudas secundarias e historial con regreso al contexto exacto.
4. Completar Consejos, Referencias y ejercicios de Aprende.
5. Persistencia de estudios, refinamiento visual y pruebas con usuarios.

Por ahora se asume uso local individual, en español, sin cuentas ni publicación en Internet. Autenticación, servicio multiusuario, alojamiento público y entrenamiento propio quedan fuera de esta primera etapa, salvo que el usuario cambie la prioridad.

## Preguntas de contexto

Puedes responder aquí o en el chat; no hace falta contestarlas todas para seguir con la integración técnica.

| Pregunta | Por qué importa | Supuesto provisional |
| --- | --- | --- |
| ¿Es una tesis/investigación, una demostración académica o un producto para uso cotidiano? ¿Hay fecha de entrega? | Determina entregables y prioridad de validación | Prototipo educativo funcional; fecha sin definir |
| ¿Qué nivel tienen los usuarios y qué edades aproximadas? | Ajusta vocabulario, profundidad y diseño de ejercicios | Personas adultas principiantes/intermedias, por confirmar |
| ¿El primer entregable se usará solo en tu PC o también por otras personas desde sus equipos? | Determina arquitectura, concurrencia y despliegue | Local en tu PC |
| ¿Hay partidas PGN y ejemplos de errores que debamos usar como casos de prueba? | Permite contrastar resultados con necesidades reales | Partida incluida y casos de prueba técnicos |
| ¿Existen conclusiones de entrevistas o criterios de evaluación que debamos respetar? | Vincula los tres recorridos con evidencia de usuarios | Solo el contexto pegado en esta conversación |

No se han revisado los textos completos de los cuatro artículos ni la presentación mencionada en la conversación original. Si el entregable requiere fundamentación académica, hará falta consultar esos materiales y verificar las atribuciones antes de redactarla.

## Fuentes técnicas consultadas

- [Qwen3 4B en Ollama: tamaño, cuantización y licencia](https://ollama.com/library/qwen3:4b).
- [Qwen3 8B en Ollama](https://ollama.com/library/qwen3:8b).
- [Licencia del modelo Qwen3 4B](https://huggingface.co/Qwen/Qwen3-4B/blob/main/LICENSE).
- [API de chat de Ollama](https://docs.ollama.com/api/chat).
- [Descargas oficiales de Stockfish](https://stockfishchess.org/download/).

La recomendación de hardware es una inferencia a partir de la memoria disponible y los tamaños de los modelos, pendiente de medición local.
