## Anti-cheat a nivel de kernel
#### 1. Conceptos básicos

##### 1.1 ¿Qué significa que un anti-cheat trabaje a nivel de kernel?

Los anti‑cheat que operan a nivel de kernel (“kernel‑mode anti‑cheat”) tienen acceso privilegiado al sistema operativo, lo que les permite hacer inspecciones profundas y monitorear actividades sospechosas que un usuario estándar no podría detectar.
##### 1.2 Arquitectura general

Un anti‑cheat moderno tiene módulos en modo usuario  y uno o más módulos en modo kernel que trabajan juntos.

1. **Modulo kernel**: Actúa como "vigilante de bajo nivel", intercepta eventos del sistema (creación de procesos, carga de controladores o módulos, hooks de funciones del kernel, acceso a memoria de otros procesos, etc.).
2. **Módulo modo usuario**: Se comunica con el kernel para configurar reglas, enviar logs, recibir alertas, ejecutar scans de memoria, pasar resultados al servidor remoto o backend, etc.

También hay un componente backend (servidor central) que recoge métricas, actualizaciones de reglas, listas negras, sanciones, etc.

<u>Algunas de las técnicas usadas son</u>: Escaneo de memoria y de procesos, monitoreo de carga de módulos, hooking, sandboxing.

##### 1.3 ¿Son los anti-cheat rootkits?

Es bastante común que algunas funciones del anti‑cheat se parezcan a rootkits, por lo que hay debates éticos y de seguridad al respecto.

El siguiente articulo habla sobre esto: [“If It Looks Like a Rootkit and Deceives Like a Rootkit: A Critical Examination of Kernel-Level Anti-Cheat Systems”](https://arxiv.org/abs/2408.00500)

#### 2. Funcionamiento de anti-cheat famosos

##### 2.1 BattlEye

Se describe como un sistema de protección “proactiva basada en kernel” que realiza escaneos dinámicos y permanentes en modos de usuario y kernel con detección específica y genérica. [Fuente](https://www.battleye.com/about).

En su FAQ, BattlEye advierte que bloquea software que use drivers de kernel con vulnerabilidades conocidas. [Fuente](https://www.battleye.com/support/faq).

Componentes que se han deducido que tiene BattlEye:

| Componente                            | Modo                      | Rol reportado / función                                                                                                                                       |
| ------------------------------------- | ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **BEDaisy**                           | Kernel driver             | Realiza detecciones a bajo nivel en el kernel, monitorea controladores cargados, módulos, callbacks del sistema, excepciones, y recopila eventos sospechosos. |
| **BEClient (DLL)**                    | Modo usuario              | Comunica con el driver de kernel, envía solicitudes de lectura/consulta, recibe eventos detectados, integra con el cliente de juego.                          |
| **BEService / Servicio de sistema**   | Modo usuario              | Maneja la comunicación con el backend de BattlEye, realiza actualizaciones, coordina operaciones de cliente/driver.                                           |
| **BEServer (infraestructura remota)** | N/A (servidores externos) | Recibe reportes de detección, mantiene la lógica de baneos, actualizaciones, firmas, heurísticas centrales.                                                   |

La información se ha sacado de esta [página](https://www.unknowncheats.me/forum/anti-cheat-bypass/505404-battleye-kernel-module-detection-depth-analysis.html) resumida mediante ChatGPT.
##### 2.2 Easy Anti-Cheat (EAC)

El driver de EAC escanea drivers cargados en el sistema, busca+ módulos conocidos de herramientas de trampas (por ejemplo _Cheat Engine_) y controla la integridad del código del driver.

Algunas técnicas que se han descubierto son:

| Técnica                                              | Qué hace / para qué                                                                                                                                                                                                              |
| ---------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Escaneo de memoria**                               | EAC revisa la memoria del proceso del juego y zonas adyacentes para detectar cheats cargados o manipulaciones.                                                                                                                   |
| **Detección de hooks (ganchos)**                     | Busca modificaciones del flujo normal del juego vía hooks engañosos, por ejemplo de librerías externas, o manipulaciones de funciones.                                                                                           |
| **Escaneo de drivers / módulos del sistema**         | EAC puede identificar drivers maliciosos o no firmados que se usan para trampas.                                                                                                                                                 |
| **Autoprotección (self-protection)**                 | EAC implementa mecanismos para asegurar su propio código: comprobaciones de integridad, detección de alteraciones, posiblemente ofuscación, y tareas similares para impedir reverse engineering o modificaciones del anti-cheat. |
| **Uso de virtualización / instrucciones especiales** | En el estudio se menciona que EAC utiliza una máquina virtual propietaria.                                                                                                                                                       |

La información se ha sacado de esta [página](https://arxiv.org/html/2408.00500v1) resumida mediante ChatGPT.

El [estudio](https://arxiv.org/html/2408.00500v1?utm_source=chatgpt.com) que se ha mencionado antes evalúa hasta qué punto los anti-cheat de kernel se parecen a rootkits. Puntos relevantes para EAC:

- EAC obtiene un alto nivel de privilegio, ya que el driver kernel puede leer memoria, detectar módulos desconocidos, hooks, etc. Esto es precisamente lo que hace que algunos lo consideren como software de muy profundo acceso.
- Su self-protection y esfuerzo por ocultar y modificar su propio código son vistas como similares a comportamientos que puede hacer los rootkits.

##### 2.3 RICOCHET

RICOCHET Anti-Cheat es una iniciativa multifacética que incluye herramientas del lado servidor para monitorizar analytics, procesos de investigación mejorados, detecciones y mitigaciones, seguridad de cuentas, etc.  En la mayoría de títulos de Call of Duty desde Modern Warfare II hasta Black Ops 6 se utiliza un driver de nivel kernel en PC, desarrollado internamente por el equipo de Call of Duty. 

Ese controlador kernel solo esta activo cuando se esta jugando a ese juego, y se apaga cuando cierras el juego. No está siempre activo si no estás jugando a un videojuego en particular que requiera ese anti-cheat.

El driver supervisa, monitorea y reporta aplicaciones que intentan interactuar con los juegos protegidos por RICOCHET para detectar procesos no autorizados que podrían estar manipulando el juego. 

Toda la información esta sacada de la pagina oficial de Activision en el apartado [Ricochet](https://www.callofduty.com/es/modernwarfare2/ricochet) y también de su [pagina de soporte](https://support.activision.com/content/atvi/support/web/en_au/articles/ricochet-overview.html)

No hay mucha mas información al respecto de este anti-cheat mas allá de la que hay en medios oficiales de Activision.

## Fallo de Crowdstrike en Julio de 2024

#### 1. ¿Qué pasó?

Sucedió concretamente el 19 de Julio del año 2024 exactamente a las 04:09 de la madrugada UTC. El problema vino a raíz de una actualización distribuida por Crowdstrike con una configuración defectuosa.

Lo que paso de forma mas técnica fue que la actualización venia con un cambio en un canal, concretamente en el "Channel File 291", debido a ese cambio el código del sensor intentaba realizar una lectura de memoria fuera de los límite válidos que a su vez generaba una violación de acceso, como consecuencia muchas maquinas entraron en un bucle de arranque. 

Solo afectaba a Windows por lo que los sistemas Mac y Linux se salvaron de este error. Se estima que unos 8 millones y medio de sistemas quedaron afectados

#### 2. ¿Qué consecuencias tuvo?

Los sectores mas afectados fueron las aerolíneas lo que provoco muchas cancelaciones de vuelos, hospitales, bancos, instituciones publicas entre otras.

Uno de los casos mas destacados fue la aerolínea "Delta Air Lines", tuvo que cancelar 7000 vuelos durante los siguientes días, se vieron afectados más de un millón de personas.

Se calculan una perdida de mas de 5 mil millones de dólares para las grandes empresas.

Obviamente como suele pasar en estos casos la empresa mas afectada fue "Crowdstrike" mediante la perdida de confianza y criticas publicas.

#### 3. ¿Cómo se arreglo?

CrowdStrike revirtió la actualización a las 05:27, 78 minutos después de lanzarla. Se publico un reporte explicando que había pasado y a quienes habían afectado de manera preliminar, pasando los días hicieron ya un RCA (Root Cause Analysis). 

Muchas organizaciones para resolver el problema tuvieron que arrancar en modo seguro y eliminar ciertos archivos de configuración con este formato "C-00000291*.sys".

Los sistemas que usaban BitLocker tuvieron una recuperación más complicada ya que requerían de una clave de 48 dígitos que estaba guardada en un servidor que también se había visto afectado.

#### 4. Fuentes

La información se ha sacado de las siguientes páginas web resumidas y explicadas gracias a ChatGPT:
- [Incidente de CrowdStrike](https://es.wikipedia.org/wiki/Incidente_de_CrowdStrike_de_2024) (Wikipedia)
- [Preliminary Post Incident Review](https://www.crowdstrike.com/en-us/blog/falcon-content-update-preliminary-post-incident-report/) (CrowdStrike Blog)
- [CrowdStrike outage explained: What caused it and what’s next](https://www.techtarget.com/whatis/feature/Explaining-the-largest-IT-outage-in-history-and-whats-next) (TechTarget)
- [CrowdStrike faces federal scrutiny following global Windows outage](https://siliconangle.com/2025/06/04/crowdstrike-faces-federal-scrutiny-following-global-windows-outage/) (siliconANGLE)
