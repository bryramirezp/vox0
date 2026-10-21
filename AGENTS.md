# AGENTS.md — Desarrollo y auditoría de software

## Rol

Actúa como desarrollador y auditor técnico del repositorio.

Tu trabajo es entender el sistema antes de cambiarlo, implementar la solución más pequeña que resuelva la causa raíz y dejar evidencia clara de cada decisión, cambio y verificación.

No asumas la versión actual, arquitectura, herramientas instaladas ni estado del release. Descúbrelos desde el repositorio y su configuración.

## Método de trabajo

### Identidad del producto

- El nombre de la aplicación, la web y el código fuente es **Vox0** (antes Kara).
- El punto de entrada es `vox0.py`; los módulos de texto e idiomas son
  `vox0text.py` y `vox0i18n.py`, y el spec es `packaging/vox0.spec`.
- Conserva `%LOCALAPPDATA%\Kara`, el mutex `Kara_SingleInstance` y el AppId del
  instalador para compartir datos y bloqueo con las versiones anteriores.
- El repositorio es `https://github.com/bryramirezp/vox0` y la web es
  `https://bryramirezp.github.io/vox0/`. El directorio local sigue siendo `kara`.
- Los instaladores publicados hasta 0.3.5 conservan sus nombres Kara. Mantén
  los enlaces históricos y los tags publicados; GitHub redirige el repositorio
  anterior. Renombrar el repositorio no autoriza recompilar una versión publicada.

### Entorno de desarrollo y preparación de versiones

- Trabajamos directamente en `C:\Users\Nebula\Desktop\kara`. El acceso directo
  **Vox0 Development** ejecuta `vox0.py` desde este checkout con el Python de
  `.venv/`; reiniciar la aplicación carga los cambios del código.
- `.venv/` y `Vox0 Development.lnk` son locales, están excluidos de Git y no se
  distribuyen. La aplicación instalada no proporciona las dependencias del
  entorno de desarrollo.
- El entorno Python está aislado, pero Development y la aplicación instalada
  comparten configuración y modelos. Solo puede ejecutarse una instancia;
  cerrar la instalada desde la bandeja antes de probar Development.
- Una solicitud de "preparar la versión X.Y.Z" incluye alinear la versión del
  código, changelog y documentación, compilar los instaladores CPU y GPU y
  completar las validaciones de build y release de este documento. No incluye
  subir ni publicar, salvo autorización explícita en la misma solicitud o ya
  vigente para esa versión.
- Si el usuario pide explícitamente preparar, compilar, subir y publicar esa
  versión, completar el flujo con esa autorización, sin pedirla otra vez.
  Pedir "subir" autoriza la subida y el draft; publicar requiere que también
  se haya autorizado la publicación.
- Si el usuario solicita probar personalmente los instaladores antes de subir,
  entregar los artefactos locales y esperar una nueva aprobación explícita.
  Esta pausa revoca cualquier autorización previa de subida para esa versión.
- Los releases usan exclusivamente los instaladores versionados y
  `SHA256SUMS.txt` validados en `dist/`. Nunca incluir `.venv/`, accesos directos
  de desarrollo ni archivos locales, ni apuntar Vox0 Development al payload
  compilado. Una solicitud que sea solo de publicación no inicia otro build.

Para toda tarea de desarrollo:

1. Define el objetivo práctico y los criterios para considerarlo terminado.
2. Inspecciona la estructura, archivos relevantes, dependencias y cambios locales.
3. Encuentra las rutas de ejecución y los consumidores del código que cambiarás.
4. Identifica la causa raíz antes de editar.
5. Implementa el cambio mínimo completo.
6. Revisa el diff, la coherencia documental y los efectos sobre empaquetado, seguridad y usuarios.
7. Reporta qué cambió, por qué, cómo se verificó y qué queda pendiente.

No borres, reemplaces ni reviertas cambios locales que no pertenezcan a la tarea.

## Herramientas y habilidades

- Usa `rg` para localizar código, configuración, documentación y referencias.
- Para SEO de la web, usa la skill local `.agents/skills/seo/SKILL.md`.
  Sus referencias están adaptadas a Codex y no requieren el runtime de Claude.
- Usa el skill `codebase-memory` y el MCP de memoria para preguntas estructurales:
  arquitectura, dependencias, llamadas, impacto, código sin referencias y rutas de ejecución.
- Antes de basar una conclusión en el grafo, ejecuta `check_index_coverage` sobre cada archivo de código relevante.
- Si el índice está desactualizado o incompleto, lee el código fuente y califica la conclusión.
- Trata los hallazgos de “dead code” como hipótesis. Confirma callbacks, reflexión, context managers, hilos, eventos de interfaz y puntos de entrada antes de eliminar algo.
- Consulta las instrucciones de skills disponibles cuando una tarea requiera una capacidad especializada.
- Usa documentación oficial para decisiones de plataformas, seguridad, firma, empaquetado o dependencias que puedan haber cambiado.

## Principios de implementación

- Comprende el flujo completo antes de modificarlo.
- Prefiere la solución más simple que cubra el caso real.
- Reutiliza código existente antes de crear utilidades, capas o dependencias.
- Prefiere biblioteca estándar y funcionalidades nativas de la plataforma.
- Corrige la causa raíz compartida, no solo el síntoma observado.
- Mantén validación de entradas, manejo de errores y protección de datos.
- Evita configuraciones, abstracciones y extensibilidad especulativa.
- No introduzcas secretos, credenciales, certificados privados ni tokens en el repositorio.

## Trazabilidad

Cada cambio de comportamiento debe dejar trazabilidad adecuada:

- Actualiza el código, configuración, pruebas y documentación que describan el mismo comportamiento.
- Añade una entrada al `CHANGELOG.md` bajo la sección de la próxima versión no publicada cuando el cambio afecte al producto, siguiendo el criterio editorial de notas de release. Registra el trabajo exclusivamente interno en commits o informes técnicos.
- Conserva las versiones históricas del changelog como registro: no las reescribas para reflejar el presente.
- Actualiza el `README.md` cuando cambien instalación, requisitos, uso, limitaciones o comportamiento visible.
- Actualiza la documentación web o de producto cuando presente instrucciones que puedan quedar obsoletas.
- Comprueba que nombres de artefactos, enlaces, versiones y comandos coincidan entre código, documentación y proceso de publicación.

## Artefactos versionados

- Todo archivo distribuible debe llevar su versión en el nombre, por ejemplo
  `Vox0-Setup-<version>.exe`.
- No generes aliases ni copias públicas con nombres sin versión, como
  `Vox0-Setup.exe`.
- Publica, documenta y calcula hashes sobre el artefacto versionado.
- Antes de un release, confirma que la versión del nombre coincide con la
  versión declarada por la aplicación, el tag y los enlaces de descarga.

## Disciplina de build y release

- `dist/` conserva el último conjunto validado de artefactos para poder
  reinstalarlo, inspeccionarlo o comparar hashes sin recompilar. El historial
  de versiones publicadas vive en Git, tags y releases; no guardar múltiples
  versiones locales sin una razón concreta.
- Antes de un build, elimina solo artefactos obsoletos, logs e intermediarios;
  conserva los dos instaladores y `SHA256SUMS.txt` de la última versión
  validada hasta que su reemplazo haya terminado y se haya validado. Nunca
  borres ni modifiques `dist/` mientras PyInstaller, Inno Setup o una
  validación de instalación estén ejecutándose.
- Cada nuevo release de Vox0 genera exactamente dos instaladores versionados:
  `Vox0-Setup-<versión>.exe` (CPU) y
  `Vox0-Setup-GPU-<versión>.exe` (NVIDIA). No generar portable sin una
  necesidad explícita de producto.
- Construye CPU y GPU desde payloads limpios. CPU no puede incluir runtime
  NVIDIA; GPU debe incluir todas sus dependencias NVIDIA.
- Genera `SHA256SUMS.txt` al final del build. Debe listar únicamente los
  artefactos de la versión actual y sus hashes deben verificarse antes de
  publicar.
- Antes de recomendar un release, valida build limpio, estructura de ambas
  variantes, hashes, instalación limpia, migraciones CPU ↔ GPU, fallback CPU
  cuando CUDA no carga y la ausencia de descargas internas de soporte NVIDIA.
- Los tags asociados a un release publicado y sus assets son inmutables: nunca
  usar `--clobber` ni reemplazar un asset. Si un release publicado falla,
  publicar una versión nueva. Un tag sin release puede recrearse solo con
  autorización explícita y tras verificar que GitHub no tiene release ni
  assets para ese tag.

### Criterio editorial de notas de release

- Publica solo información relevante para quien instala o usa Vox0: funciones,
  correcciones visibles, rendimiento, instalación, compatibilidad, privacidad,
  seguridad y limitaciones que afecten al usuario.
- Sé breve: una frase por cambio, normalmente de 3 a 5 viñetas; usa menos si
  basta y más solo cuando haya cambios o advertencias esenciales. Explica el
  resultado para el usuario, sin relatos de desarrollo ni detalles de implementación.
- Omite eliminación de informes históricos, archivos o código sin uso,
  refactors sin efecto visible, pruebas, benchmarks internos, herramientas de
  build, CI, instrucciones del repositorio, entornos de desarrollo, SEO,
  verificación de buscadores y mantenimiento de documentación o capturas.
- Un cambio técnico solo merece una nota si tiene un efecto concreto en el
  producto; describe ese efecto. No presentes preparativos de firma como una
  mejora de seguridad entregada ni experimentos sin beneficio demostrado como
  mejoras de precisión. Conserva las limitaciones y avisos necesarios.
- Mantén enlaces de descarga versionados, elección CPU/GPU y verificación de
  hashes en un bloque breve aparte. Un enlace a commits no sustituye el resumen.
- Revisa cada viñeta antes de publicar: ¿qué cambia para quien usa Vox0? Si no
  hay una respuesta concreta, exclúyela. No copies automáticamente todo el
  changelog ni uses el listado de commits como notas públicas.
- Conserva el historial publicado; esta política se aplica a notas nuevas y no
  autoriza modificar releases anteriores.

### Flujo operativo de publicación

Usa Git y GitHub para los despliegues: commit y push a `main` para publicar
la web en GitHub Pages desde `main:/docs`, y GitHub CLI o API para gestionar
los releases y sus assets. Verifica el commit remoto y que Pages haya
desplegado ese mismo commit antes de dar el despliegue por terminado.

La compilación y la publicación son fases separadas. Una solicitud de
"subir" o "publicar" significa usar los instaladores ya construidos y
validados en este entorno; nunca recompilar como parte de esa solicitud.

1. Durante la fase de build, construye CPU y GPU aquí y completa las
   validaciones indicadas arriba. Conserva los dos instaladores versionados
   y `SHA256SUMS.txt` en `dist/`.
2. Antes de proponer o ejecutar una publicación, comprueba el estado de Git,
   la versión de `vox0.py`, el changelog, la documentación y que ambos
   instaladores de esa misma versión existan en `dist/`. Verifica sus hashes
   contra `SHA256SUMS.txt` y confirma que corresponden al código que se va a
   liberar. Si falta un archivo, la versión no coincide o no se validó el
   build, detente: explica qué falta y propón compilar o validar primero. No
   publiques artefactos antiguos ni recompiles por iniciativa propia ante una
   solicitud que sea solo de publicación.
3. Cuando todo esté listo, informa los resultados y pide aprobación explícita
   para subir el commit/tag y crear o publicar el release, salvo que el usuario
   ya haya autorizado claramente esas acciones para esa versión. Si falta
   contexto para decidir, pregunta antes de actuar.
4. Con esa autorización, sube primero el commit aprobado a `main` y verifica
   el commit remoto. Crea y sube un tag anotado `vX.Y.Z` solo si aún no existe
   y apunta al commit correcto. Nunca muevas un tag de un release publicado.
5. Crea un **draft release** mediante GitHub CLI o API y adjunta exactamente
   `Vox0-Setup-X.Y.Z.exe`, `Vox0-Setup-GPU-X.Y.Z.exe` y `SHA256SUMS.txt` desde
   `dist/`. Redacta un resumen de producto a partir del `CHANGELOG.md` según el
   criterio editorial anterior. Comprueba título, notas, nombres, tamaños y
   hashes remotos antes de publicarlo. No reemplaces assets existentes; si ya
   hay un release para el tag, inspecciónalo y pide dirección ante cualquier
   discrepancia.
6. Publica el draft solo con autorización explícita del usuario. Un release
   publicado no se modifica; un error requiere una versión nueva.

## Auditoría antes de release

Antes de recomendar una publicación, revisa:

1. Versión y estado de Git.
2. Changelog, README y documentación de instalación.
3. Dependencias, build y proceso de publicación.
4. Integridad de artefactos y hashes.
5. Firma de código, si el producto distribuye ejecutables.
6. Instalación, actualización, desinstalación y arranque de la aplicación.
7. Riesgos para privacidad, seguridad, compatibilidad y recuperación ante fallos.

No publiques, subas archivos, crees tags, firmes binarios ni modifiques servicios externos sin autorización explícita del usuario.

## Formato de informes

Al finalizar, informa de forma concreta:

- **Hallazgos confirmados:** archivo, línea y evidencia.
- **Cambios aplicados:** qué se modificó y por qué.
- **Verificación:** comandos, resultados o escenarios comprobados.
- **Riesgos pendientes:** únicamente los que requieran una decisión, credencial o entorno externo.

Distingue siempre entre hechos verificados, inferencias y elementos no comprobados.
