#### 📋 Descripción

Es una herramienta modular educativa para la recopilación y análisis de información pública (Open Source Intelligence). Permite investigar dominios, correos electrónicos y nombres de usuario utilizando diversas fuentes legales y abiertas.

#### ⚙️ Características principales

**Diseño modular:** cada fuente de información se implementa como un módulo independiente con la firma:
```bash
run(target, config) -> dict
```

**Fuentes integradas:**
- **HaveIBeenPwned:** búsqueda de brechas y pastes asociadas a un email.
- **WHOIS:** información de registro de dominios.
- **DNS:** resolución de registros A, MX, TXT, NS, SOA, CNAME.
- **Metadatos de dominio:** título, meta tags, favicon y encabezados HTTP.
- **Presencia de usuario:** búsqueda básica de nombre de usuario en GitHub, Reddit, Twitter, Instagram y Keybase.

#### 💻 Instalación y uso

##### 🔧 Requisitos previos

- **Python:** 3.9 o superior
- Estas son las dependencias necesarias:
```bash
pip install requests dnspython python-whois beautifulsoup4 Flask lxml
```
- Opcional (para HaveIBeenPwned), añadir tu API key en la variable de entorno o en el archivo de configuración:
```bash
export HIBP_API_KEY="tu_api_key"
```

##### 🚀 Instalación y ejecución

1. Clona o descarga el proyecto
```bash
git clone https://github.com/tuusuario/osint-modular-tool.git
cd osint-modular-tool
```
2. Instala dependencias (usar el comando anterior si no tienes un `requirements.txt`.)
```bash
pip install -r requirements.txt
```
3. Ejecuta el servidor Flask
```bash
python osint_tool.py
#Si todo está correcto, verás:
* Running on http://127.0.0.1:5000
```

##### 🌐 Uso desde el navegador

Abre en tu navegador:
👉 [http://127.0.0.1:5000](http://127.0.0.1:5000)
Aparecerá un formulario donde puedes introducir:
- Email
- Domain
- Username
Ejemplo rápido:
```
Email: prueba@ejemplo.com 
Domain: ejemplo.com 
Username: usuarioprueba
```

#### 🧠 Estructura del proyecto

```
osint_tool.py
│
├── Módulos principales:
│   ├── module_hibp()       → HaveIBeenPwned API
│   ├── module_whois()      → WHOIS lookup
│   ├── module_dns()        → DNS resolver
│   ├── module_meta()       → HTTP metadata parser
│   ├── module_username()   → Username footprint
│
├── build_report()          → Ejecuta los módulos según los targets
├── report_to_graphml()     → Exporta el informe a GraphML (Maltego compatible)
└── Flask UI                → /, /run, /api/run, /export/graphml
```

#### 🧪 Pruebas rápidas

Desde el formulario web:
- Abre [http://127.0.0.1:5000](http://127.0.0.1:5000)
- Ingresa un dominio o correo.
- Pulsa **Run** y analiza la salida JSON.

Desde la terminal (API REST):
```bash
curl -X POST http://127.0.0.1:5000/api/run \
  -H "Content-Type: application/json" \
  -d '{"domain": "example.com"}'
```

O en PowerShell:
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/run" `
  -Method Post -Body '{"domain":"example.com"}' `
  -ContentType "application/json"
```

##### 🧭 Resultados esperados

| Módulo            | Descripción                        | Ejemplo              |
| ----------------- | ---------------------------------- | -------------------- |
| `module_hibp`     | Consulta brechas en HaveIBeenPwned | Requiere API key     |
| `module_whois`    | WHOIS de un dominio                | tajamar.es           |
| `module_dns`      | Registros DNS                      | ejemplo.com          |
| `module_meta`     | Metadatos del sitio                | ejemplo.com          |
| `module_username` | Presencia en redes                 | github, reddit, etc. |

#### 🧾 Exportación a GraphML

Puedes generar un archivo compatible con Maltego, esto creará una red visual con las relaciones entre objetivos y módulos.:
```bash
curl -X POST http://127.0.0.1:5000/export/graphml \
  -H "Content-Type: application/json" \
  -d @reporte.json --output report.graphml
```

#### 🧰 Modo depuración

```python
if __name__ == '__main__':
    app.run(port=5000, debug=True)
```

#### ⚖️ Aviso legal y ético

- Esta herramienta está diseñada exclusivamente con fines educativos y de investigación legítima.  
- No debe emplearse contra objetivos sin autorización previa.
- El autor no se responsabiliza por el uso indebido del código. 
- Cumple siempre las leyes y políticas de privacidad aplicables en tu jurisdicción.

#### 👥 Autores

Realizado por: Enrique Aguilar Michán, Juan de la Asunción Cantalejo e Iván Fernández Aguilera.

#### 📄 Licencia

Este proyecto se distribuye bajo la licencia MIT.


