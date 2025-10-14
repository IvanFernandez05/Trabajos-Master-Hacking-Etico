Realizado por: Enrique Aguilar Michán, Juan de la Asunción Cantalejo e Iván Fernández Aguilera.

#### 1.1 Imágenes / Vídeos / Documentos

Objetivo: extraer información visual o metadatos ocultos.
Herramientas/API sugeridas:
- CompreFace API → reconocimiento facial y coincidencias.
- ExifTool (local o librería Python) → extracción de metadatos EXIF de imágenes y vídeos.
- Luxand Cloud API → detección de caras y comparación con una base de datos previa.
Acciones:
- Buscar coincidencias faciales o de objetos.
- Extraer metadatos (geolocalización, dispositivo, fecha, software).
- Analizar texto incrustado (OCR con Tesseract o Google Vision API Free Tier).
Resultados esperados:
- Identificación visual.
- Origen o contexto del archivo.
- Posibles vínculos con otros archivos o fuentes.
 
#### 1.2 Redes Sociales

Objetivo: obtener huella digital del sujeto o alias.
Herramientas/API sugeridas:
- Social Searcher API o Social Analyzer (GitHub).
- Apify Social Media Finder.
Acciones:
- Buscar el alias, nombre o correo en redes (Twitter/X, Facebook, Instagram, Reddit, etc.).
- Extraer datos públicos: nombre, bio, ubicación, enlaces, frecuencia de actividad.
- Recopilar URLs de publicaciones, seguidores, relaciones cruzadas.
Resultados esperados:
- Lista de perfiles potenciales.
- Mapas de relaciones o patrones de comportamiento digital.
- Posible identificación de la persona o entorno.
 
#### 1.3 Motores de búsqueda de personas

Objetivo: verificar identidad y obtener información contextual.
Herramientas/API sugeridas:
- Epieos (correo / teléfono).
- Social Links API.
- Pipl API o WhoIsXML People Data (si tuvieras acceso).
Acciones:
- Buscar combinaciones de nombre + ubicación + email.
- Verificar si aparecen coincidencias en registros públicos, foros, leaks o redes.
- Extraer dominios, correos alternativos o direcciones asociadas.
Resultados esperados:
- Perfil consolidado de la persona (nombre real, alias, ubicaciones, emails).
- Posibles conexiones con redes sociales o sitios de trabajo.
 
#### 1.4 Números de teléfono

Objetivo: validar y enriquecer datos de un número.
Herramientas/API sugeridas:
- Numverify o NumLookupAPI.
- Twilio Lookup (básico gratuito).
Acciones:
- Verificar formato, país, operador y tipo de línea.
- Buscar si el número está vinculado a perfiles públicos (por ejemplo, en redes o leaks).
- Correlacionar con correos o nombres encontrados.
Resultados esperados:
- Confirmación de validez del número.
- Posible vinculación con nombre o red social

#### 1.5 Username

Objetivo: Identificar la presencia o uso de un alias en distintas plataformas y servicios para establecer huella digital y actividad pública.
Herramientas/APÎ sugeridas:
- Sherlock (GitHub) → Búsqueda automatizada de nombres de usuario en cientos de sitios.
- Namechk API (Free Tier) → Verificación de disponibilidad o existencia de usernames en redes y dominios.
- WhatsMyName (OSINT project) → búsqueda de alias en sitios web populares con API REST ligera.
Acciones:
- Consultar las APIs para comprobar si un nombre de usuario existe en distintas plataformas.
- Analizar metadatos de perfiles (biografía, enlaces, ubicación, foto).
- Correlacionar alias similares en diferentes sitios (por ejemplo, “juanperez_”, “juan.perez”).
- Cruzar resultados con redes sociales, foros o leaks públicos.
Resultados esperados:
- Lista de cuentas activas o registradas con ese alias.
- Identificación de la plataforma principal del usuario.
- Posible vínculo entre perfiles y alias alternativos.
 
#### 1.6 Email Address

Objetivo: Verificar la validez, reputación y posibles exposiciones públicas o leaks asociadas a un correo electrónico.
Herramientas/API sugeridas:
- Hunter.io API (Free Tier) → Verificación de emails y búsqueda por dominio.
- Have I Been Pwned API (HIBP) → Detección de exposición en brechas de datos públicas.
- EmailRep.io (Free API) → Reputación y contexto de uso de un correo (spam, leaks, social profiles).
Acciones:
- Validar formato, existencia y servidor MX.
- Consultar bases públicas para detectar filtraciones.
- Extraer información contextual (redes sociales asociadas, confianza, frecuencia de uso).
- Clasificar correos corporativos vs. personales según dominio
Resultados esperados:
- Estado del correo (válido, falso o comprometido).
- Contexto digital (corporativo, spammer, leak).
- Relaciones con dominios, nombres o perfiles.
 
#### 1.7 Domain name

Objetivo: Analizar infraestructura, reputación, historial y huella técnica de un dominio.
Herramientas/API sugeridas:
- WhoisXML API (Free tier) → consulta WHOIS, DNS y reputación.
- VirusTotal API (Free) → reputación, subdominios, análisis de seguridad y passive DNS.
- SecurityTrails API (Community tier) →datos de DNS históricos, IPs asociadas y tecnologías usadas.
Acciones:
- Consultar registros WHOIS para obtener propietario, fechas, contacto.
- Analizar subdominios y DNS pasivos (infraestructura vinculada).
- Evaluar reputación (listas negras, puntuación de riesgo).
- Identificar tecnologías del sitio (CMS, hosting, proveedor)
Resultados esperados:
- Información técnica completa del dominio.
- Identificación de relaciones entre dominios e IPs.
- Evaluación de riesgo o exposición.
 
#### 1.8 IP & MAC Address

Objetivo: Identificar ubicación, reputación, proveedor y actividad de una dirección IP o dispositivo.
Herramientas/API sugeridas:
- ipinfo.io API (Free Tier) → geolocalización, ASN, ISP y dominio inverso.
- AbuseIPDB API (Free) → reputación y reportes de abuso asociados a una IP.
- MACVendors API (Free) → identificación del fabricante a partir de dirección MAC.
Acciones:
- Geolocalizar la IP y obtener ASN / ISP.
- Consultar si la IP ha sido reportada por spam, ataques o abuso.
- Identificar fabricante o tipo de dispositivo por prefijo MAC.
- Correlacionar IPs o MACs con redes conocidas o dominios asociados.
Resultados esperados:
- Origen geográfico y técnico de la IP/MAC.
- Nivel de confianza o riesgo.
- Posibles vínculos con dominios, servidores o actores específicos.
 
#### 1.9 Geolocation Tools / Maps

Objetivo: Obtener la ubicación geográfica aproximada de direcciones IP, coordenadas, o lugares mencionados, para correlacionar actividad digital con ubicaciones físicas.
Herramientas / API sugeridas:
- IP-API → Geolocalización IP gratuita sin clave (JSON/XML).
- ipwhois.io → Geolocalización detallada (país, ciudad, ISP, latitud/longitud).
- IPapi → Detección de ubicación, proxy/VPN y amenazas básicas.
Acciones:
- Obtener ubicación geográfica a partir de IPs o dominios.
- Enriquecer datos con información de ISP o zona horaria.
- Mapear coordenadas sobre mapas (Google Maps API o LeafletJS).
Resultados esperados:
- Identificación del país o ciudad de origen del tráfico.
- Correlación entre eventos digitales y ubicaciones geográficas.
- Detección de patrones de conexión sospechosos (VPN, TOR, proxies).

#### 1.10 Metadata

Objetivo: Extraer metadatos visibles y ocultos de páginas web, documentos o archivos multimedia para descubrir autorías, fechas, ubicaciones o software utilizado.
Herramientas / API sugeridas:
- Meta Tags API (APILayer) → Extrae metadatos de páginas web (título, descripción, Open Graph).
- Site Metadata API (Lynkmark / URL Meta) → Obtiene favicon, autor, descripción y otros datos estructurados.
- Siterelic MetaScraping API → Recolecta información enriquecida de sitios web (logos, fechas, tags).
Acciones:
- Extraer metadatos de URLs para entender su contexto y procedencia.
- Analizar encabezados y etiquetas HTML (autor, palabras clave, tecnología usada).
- Combinar con herramientas locales (ExifTool, pdfinfo) para archivos descargados.
Resultados esperados:
- Identificación del creador o entidad detrás del contenido.
- Fechas de creación o modificación del documento.
- Tecnologías empleadas o framework web.

#### 1.11 Digital Currency

Objetivo: Analizar movimientos, direcciones y patrones en criptomonedas para rastrear flujos financieros digitales sospechosos o relacionados con actividades ilícitas.
Herramientas / API sugeridas:
- CoinGecko API → Datos de precios, exchanges y volúmenes de criptomonedas.
- Etherscan API → Información de transacciones, contratos y balances en Ethereum.
- BTC.com API → Bloques, direcciones y transacciones en la blockchain de Bitcoin.
Acciones:
- Consultar direcciones para rastrear movimientos de fondos.
- Monitorear actividad de carteras vinculadas a investigaciones.
- Cruzar datos entre distintas blockchains para detectar patrones.
Resultados esperados:
- Identificación de direcciones o wallets de interés.
- Mapas de transacciones y relaciones financieras.
- Correlación con plataformas de intercambio o servicios de lavado.

#### 1.12 Malicious File Analysis

Objetivo: Analizar archivos sospechosos o URLs para detectar malware, comportamientos anómalos o vínculos con campañas maliciosas.
Herramientas / API sugeridas:
- VirusTotal API → Escaneo de archivos y URLs con múltiples motores antivirus.
- Hybrid Analysis (Falcon Sandbox) → Análisis dinámico en sandbox y reportes detallados.
- MetaDefender Cloud API → Escaneo de archivos y hashes con motores múltiples.
Acciones:
- Subir archivos o hashes para ver reputación y detección antivirus.
- Obtener reportes de comportamiento o indicadores de compromiso (IOCs).
- Comparar resultados entre motores para validar amenazas.
Resultados esperados:
- Detección de malware o código malicioso.
- Identificación de patrones o familias de malware.