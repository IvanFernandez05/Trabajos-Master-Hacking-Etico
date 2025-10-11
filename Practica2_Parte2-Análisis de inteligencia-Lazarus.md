Realizado por: Enrique Aguilar Michán, Juan de la Asunción Cantalejo e Iván Fernández Aguilera.
#### 1. ¿Quiénes son y quien los financia?

Son un conjunto de unidades expertas en ciberseguridad de Corea del Norte, se sabe que opera desde al menos 2009 y se centra en el ciberespionaje, sabotaje y campañas criminales, principalmente para obtener ingresos o apoyos a objetivos estratégicos del país.

Es un grupo creado por la inteligencia norcoreana, pero aun así utilizan estos ataques para financiarse tanto a ellos mismos como al régimen.

Están sancionados por EEUU y son monitorizados por diferentes firmas de seguridad.

#### 2. Motivos y prioridades

No es un grupo cibercriminal cualquiera ya que cuenta con una doble motivación, política y económica, al servicio del régimen de Corea del Norte. No solo busca espionaje también monetizar cada intrusión por lo que convierte al grupo en un hibrido entre APT estatal y organización criminal.

El principal motivo es financiera, desde el 2016 el grupo ha robado mas de 3000 millones de dólares en criptomonedas, que se destinan para financia el programa nuclear y de misiles balísticos.

El otro motivo está claro que es espionaje político y militar ya que Lazarus actúa como instrumento de inteligencia del régimen. Entre los ataques mas famosos de este tipo se encuentra el robo de información a Corea del Sur, Japón, EEUU y Europa, también sobre negociaciones internacionales, ONGs y medios críticos con el régimen.

#### 3. Objetivos

El principal objetivo es el financiero/cripto como hemos dicho antes, a donde atacan son a exchanges de criptomonedas, servicios DeFi, individuos ricos con cripto.

Otro objetivo que tienen es a empresas o infraestructuras, bancos, procesadores de pago, casinos, etc.

También tiene como objetivos a gobierno y defensas, en especial contra los que esta enemistado Corea del Norte.

#### 4. TTPs (tácticas, técnicas y procedimientos)

Estas son las TTPs que mas usan con la técnica MITRE que mas encaja:

**Reconnaissance**: recopilación de objetivos y credenciales (reconnaissance previo). 
**Initial Access**:
	- Spearphishing con adjuntos o links (T1566).
	- Exploit de aplicaciones públicas / vulnerabilidades 0-day (T1190).
**Execution**: ejecución de loaders y RATs (ejecutables ofuscados, macros maliciosas). (varias técnicas de ejecución: T1059, T1204).
**Persistence**: instalación de servicios, cuentas, tareas programadas (T1543, T1053).
**Privilege Escalation**: explotación local y abuso de servicios/credenciales. (T1068, T1055).
**Credential Access**: credential dumping, keylogging, recolección de tokens (T1003, T1552).
**Lateral Movement**: uso de servicios remotos (RDP, SMB) y movimiento lateral con credenciales válidas (T1021, T1078).
**Defense Evasion**: ofuscación, empaquetado, borrar rastros, uso de técnicas fileless en ocasiones (T1027 y técnicas de evasión).
**Command & Control (C2)**: infraestructura personalizada (dominios, proxys, canales cifrados) (T1071, T1095).
**Exfiltration / Impact**: exfiltración de datos y robo/transferencia de activos (T1041)

MITRE tiene un perfil público del [grupo (G0032)](https://attack.mitre.org/groups/G0032/) donde están las técnicas que usan.

#### 5. Malware, herramientas y campañas destacadas

**WannaCry (2017):**, ataque destructivo/cripto que afectó a nivel global; vinculado a unidades norcoreanas en análisis comunitario.
- Ransomware tipo worm que explotaba EternalBlue (CVE-2017-0144) en SMBv1 para propagarse automáticamente. Cifraba archivos con AES-128 + RSA-2048 y añadía la extensión .WNCRY. Usaba DoublePulsar para inyección en procesos y escaneo masivo del puerto 445/TCP. Su código compartía componentes con herramientas de Lazarus, lo que permitió su atribución.

[**AppleJeus**](https://www.cisa.gov/news-events/cybersecurity-advisories/aa21-048a): troyano usado para comprometer exchanges/usuarios de cripto, a menudo presentado como software legítimo de trading o wallet; muy usado en campañas de robo de cripto. 
- Troyano financiero distribuido como wallets o apps de trading falsas firmadas digitalmente. Descarga módulos desde su C2 cifrado HTTPS, roba claves privadas y credenciales y mantiene persistencia creando servicios o tareas. Activo en Windows, macOS y Linux, usado para robo de criptomonedas por Lazarus.

[**TraderTraitor / herramientas para robo cripto**](https://www.theverge.com/2025/1/14/24343762/north-korea-crypto-stolen-wazirx-lazarus-group): campañas que combinan trojanizadores, backdoors y técnicas de fraude social para vaciar carteras/exchanges.
- Malware modular usado en campañas de ingeniería social (“Dream Job”). Distribuido en archivos .ISO, .LNK o .JS, recopila datos del sistema, roba credenciales y claves API, y comunica con C2 mediante HTTP cifrado (RC4/AES). Vinculado a ataques contra empresas DeFi y blockchain, con persistencia por tareas programadas.

#### 6. Ataques recientes

**Campañas de robo de criptomonedas 2024–2025**: Informes y análisis financieros (Elliptic, medios) atribuyen a grupos norcoreanos en los que se incluye a Lazarus. En 2024 se documentaron grandes robos que afectaron exchanges de India y Japón y en 2025 analistas estimaron más de $2.0B en cripto robados por actores norcoreanos en el año. Se explica mejor en esta [página](https://www.theverge.com/2025/1/14/24343762/north-korea-crypto-stolen-wazirx-lazarus-group).

**Ataques a contratistas de defensa en Corea del Sur (2024)**: la policía surcoreana informó intrusiones atribuidas a equipos norcoreanos incluyendo Lazarus y otros, donde se infiltró en redes de contratistas de defensa y se robaron datos técnicos. Esto muestra la mezcla de espionaje y operaciones financieras en su portafolio. Se explica mejor en esta [página](https://www.reuters.com/technology/cybersecurity/north-korea-hacking-teams-hack-south-korea-defence-contractors-police-2024-04-23/).
