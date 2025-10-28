#### Fase 1 - Fase de Planificación y Preparación

###### Objetivo:
Esta es una fase muy importante que cuanta mas experiencia tengas mejor sabrás como hacerla, lo fundamental es saber exactamente como es a lo que quieres hacer un pentesting, así podrás calcular los días que serán necesarios para la prueba y el precio que vas a cobrar.

#### Fase 2 - Fase de Reconocimiento

###### Objetivo:
Obtener información de un manera pasiva de nuestro objetivo.

###### ¿Qué información buscar?:
- Dominios y subdominios
- Nombres de trabajadores o jefes
- Correos
- Tecnología que se usa en cierta aplicación.

###### Posibles herramientas que usar:
- Google Dorking
- Shodan
- WHOIS

#### Fase 3 - Fase de Escaneo y Enumeración

###### ¿Qué información buscar?:
- Puertos abiertos
- Servicios activos
- Usuarios
- Recursos compartidos

###### Posibles herramientas que usar:
- nmap
- Nikto
- Nessus
- Nuclei

#### Fase 4 - Fase de Evaluación de Vulnerabilidades

###### Objetivo:
Detectar las vulnerabilidades conocidas y los posibles fallos de seguridad que puede haber.

###### ¿Qué información buscar?:
- Versiones vulnerables
- Configuraciones insegura
- Falta de actualizaciones

###### Posibles herramientas que usar:
- Metasploit
- Burpsuite

#### Fase 5 - Fase de Explotación

###### Objetivo:
Comprobar si las vulnerabilidades que hemos detectado pueden ser explotadas.

###### ¿Qué información buscar?:
- Vulnerabilidad que nos permita acceso inicial
- Vulnerabilidad que nos permita escalar privilegios
- Vulnerabilidad que nos permita ejecutar código

###### Posibles herramientas que usar:
- Metasploit
- Burpsuite
- sqlmap
- Hydra

#### Fase 6 - Fase de Post-Explotación

###### Objetivo:
Analizar el impacto del acceso que hemos obtenido y mantener la persistencia en el caso de que este permitido por contrato.

###### ¿Qué información buscar?:
- Credenciales
- Hashes
- Archivos con contenido sensible
- Movimiento lateral

###### Posibles herramientas que usar:
- Meterpreter
- Mimikatz
- Bloodhound
- CrackMapExec

#### Fase 7 - Fase de Reporte

###### Objetivo:
Documentar los resultados y como hemos llegado a ellos, proponer como corregir las vulnerabilidades explotadas.


#### Fase 8 - Fase de Remediación y Seguimiento
###### Objetivo:
Comprobar que las correcciones han sido aplicadas y funcionan correctamente.