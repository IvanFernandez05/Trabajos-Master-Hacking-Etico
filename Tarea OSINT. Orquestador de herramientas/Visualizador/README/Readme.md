
# Visualizador OSINT Web

## Descripción

Este proyecto permite visualizar de forma gráfica los datos obtenidos de un orquestador OSINT.  
El `visualizador_web` toma un archivo **.JSON** con **entidades** y **relaciones** y genera un **grafo interactivo en la web**, mostrando todas las propiedades de cada entidad de manera clara con opción a exportar a un **.GRAPHML**

**Se recalca que no se generan CSV desde la web, únicamente se ve reflejada toda la información directamente en los nodos del grafo con la opción de descargar un .GRAPHML. Para poder generar .CSV consultar la guía del [[#Visualizador de JSON OSINT (Local)]]** 

El proyecto utiliza:

- **Python 3**
- **Flask**: Para la interfaz web.
- **Graphviz**: Para generar el grafo SVG.
- **NetworkX**: Para guardar un GraphML (esto es meramente opcional)

---

## Estructura del JSON

El JSON debe contener:

- `entities`: lista de entidades, cada una con:
  - `id`: identificador único
  - `type`: tipo de entidad (`Person`, `Domain`, `Username`, `Breach`, etc.)
  - `value`: valor principal
  - `properties` *(opcional)*: diccionario con propiedades adicionales (email, phone, registrar, DNS, etc.)
- `links`: lista de relaciones entre entidades, cada una con:
  - `source`: id de la entidad origen
  - `target`: id de la entidad destino
  - `type`: tipo de relación

Ejemplo:

```json
{
  "entities": [
    {
      "id": "p1",
      "type": "Person",
      "value": "Laura Gómez",
      "properties": {
        "email": "laura.gomez@fakeemail.com",
        "phone": "+34600111222",
        "username": "laurag"
      }
    }
  ],
  "links": [
    {"source": "p1", "target": "u1", "type": "uses"}
  ]
}
```

---

## Instalación

1. Clonar el repositorio o copiar los archivos.
    
2. Instalar dependencias:

```bash
python3 -m venv venv
source venv/bin/activate
pip install flask graphviz networkx
```

![[Pasted image 20251019155841.png]]

![[Pasted image 20251019160020.png]]

**Esto es para crear un entorno virtual para evitar problemas con los paquetes del sistema o de seguridad y descargar las dependencias en el**

___

## Uso

1. Ejecutar la aplicación web:

```bash
python web_visualizador.py
```

![[Pasted image 20251019160121.png]]

- Abrir el navegador en `http://127.0.0.1:5000/`.
    
- Subir un archivo JSON con entidades y enlaces.
    ![[Pasted image 20251019163212.png]]
- El grafo se genera automáticamente y se muestra en la página:
    
    - Cada nodo representa una entidad.
        
    - Cada nodo incluye todas las propiedades en formato legible (`<BR/>` por línea).
        
    - Las relaciones entre nodos muestran el `type`.
		
        ![[Pasted image 20251019163234.png]]

___
## Cómo funciona

1. **Carga del JSON:** La aplicación Flask recibe el archivo JSON subido por el usuario.
    
2. **Procesamiento de entidades:**
    
    - Cada entidad se recorre.
        
    - Se extraen `value`, `type` y todas las `properties`.
        
    - Se construye un **label HTML** para Graphviz usando `<BR/>` por cada propiedad.
        
3. **Generación del grafo:**
    
    - Se crean nodos y enlaces usando Graphviz.
        
    - Se genera un SVG que se incrusta en la página web.
        
4. **Opcional GraphML:**
    
    - NetworkX guarda el grafo completo en `web_graph.graphml` para análisis adicional.
        
5. **Visualización:**
    
    - El usuario ve el grafo en la web, con todos los datos reflejados en los nodos de forma clara.

---

## Personalización

- Puedes cambiar **colores de nodos** o `shape` dentro de `generate_graph_from_json` agregando atributos al nodo Graphviz.
    
- Las propiedades se muestran automáticamente en cualquier JSON que siga la estructura `entities[].properties`.
    
- Los enlaces reflejan `type` tal como se define en `links`.

---

## Dependencias

- `Flask` → Para la interfaz web.
    
- `Graphviz` → Para generar el grafo SVG.
    
- `NetworkX` → Para generar GraphML.

Instalación rápida (si no lo hiciste antes):

```bash
pip install flask graphviz networkx
```

**Asegúrate de tener Graphviz instalado en el sistema, si no lo tienes:**

```bash
sudo apt install graphviz
```

![[Pasted image 20251019163446.png]]

Cuando hayamos finalizado con nuestro entorno virtual podremos salir de la siguiente manera:

```bash
deactivate
```

![[Pasted image 20251019163344.png]]

---

# Visualizador de JSON OSINT (Local)

## Descripción

Este proyecto permite visualizar los datos generados por un orquestador OSINT de manera **local**.  
El programa lee un archivo .JSON con **entidades** y **relaciones** y genera automáticamente:

- **SVG**: grafo visual de las relaciones.
- **CSV**: dos archivos (`entities.csv` y `links.csv`) para importar en Maltego.
- **GraphML**: archivo de grafo compatible con NetworkX y Maltego (aunque CSV es más fiable para Maltego ya que hay que tratar el .GRAPHML).

Cada nodo refleja las propiedades de la entidad (`email`, `phone`, `username`, `DNS`, etc.) y las relaciones muestran el tipo de conexión.

---

## Estructura del JSON

El JSON debe contener:

- `entities`: lista de entidades, cada una con:
  - `id`: identificador único
  - `type`: tipo de entidad (`Person`, `Domain`, `Username`, `Breach`, etc.)
  - `value`: valor principal
  - `properties` *(opcional)*: diccionario con propiedades adicionales
- `links`: lista de relaciones, cada una con:
  - `source`: id de la entidad origen
  - `target`: id de la entidad destino
  - `type`: tipo de relación

Ejemplo de entidad:

```json
{
  "id": "p1",
  "type": "Person",
  "value": "Laura Gómez",
  "properties": {
    "email": "laura.gomez@fakeemail.com",
    "phone": "+34600111222",
    "username": "laurag"
  }
}
```

---

## Instalación

1. Clonar el repositorio o copiar los archivos.
    
2. Crear un entorno virtual (recomendado):

```bash
python3 -m venv venv #--> en caso de que no tengas un entorno virtual
source venv/bin/activate #--> en caso de que sí lo tengas pon este comando
```

3. Instalar dependencias (si ya lo tienes instalado previamente te puedes saltar este paso y el siguiente):

```bash
pip install graphviz networkx #--> 
```

**Asegúrate de tener Graphviz instalado en el sistema, si no lo tienes:**

```bash
sudo apt install graphviz
```

---
## Uso

Ejecutar el script indicando el archivo JSON:

```bash
python visualizador_json.py --json ejemplo_orquestador.json
```

![[Pasted image 20251019163618.png]]

El programa realizará automáticamente:

1. **Generar SVG**: grafo de relaciones (`<nombre_json>_graph.svg`).
    
2. **Exportar CSV**:
    
    - `entities.csv` → contiene `id`, `type`, `value` y todas las propiedades detectadas.
        
    - `links.csv` → contiene `source`, `target`, `type` y cualquier propiedad de los enlaces.
        
3. **Exportar GraphML**: grafo completo (`<nombre_json>.graphml`), para usar en Maltego o NetworkX.


Al final, verás un resumen de los archivos generados.

---

## Cómo funciona

1. **Carga del JSON:** Se lee el archivo proporcionado por el usuario.
    
2. **Normalización de entidades y links:**
    
    - Se extraen `id`, `type`, `value` y `properties` de cada entidad.
        
    - Se extraen `source`, `target`, `type` y `properties` de cada enlace.
        
3. **Generación del grafo SVG:**
    
    - Cada nodo muestra `value`, `type` y todas sus propiedades.
        
    - Cada arista muestra `type`.
        
4. **Exportación CSV:**
    
    - Detecta dinámicamente todas las propiedades presentes y las incluye en el CSV.
        
5. **Exportación GraphML:**
    
    - Guarda el grafo completo en un formato compatible con herramientas de análisis de grafos.

---

## Personalización

- **Estilo del SVG:** Puedes modificar `shape`, `fontsize` y `color` de los nodos en la función `generate_graph`.
    
- **Nuevas propiedades:** Cualquier propiedad incluida en `entities[].properties` aparecerá automáticamente en el CSV y en el nodo SVG.
    
- **Archivo JSON:** El script es **universal**: funciona con cualquier JSON que tenga `entities` y `links`. Solo cambia el nombre o la ruta del JSON al ejecutar el script.

---

## Dependencias

- `Graphviz` → Para generar el grafo SVG.
    
- `NetworkX` → Para exportar GraphML.
    
- `csv`, `json`, `argparse`, `os` → Librerías estándar de Python.
    

Instalación rápida:

```bash
pip install graphviz networkx
```

---

## Visualización en Maltego


Abrimos la aplicación de Maltego

![[Pasted image 20251019163724.png]]


 Instalamos dependencias si es necesario

![[Pasted image 20251019164234.png]]

Importamos nuestros .CSV

![[Pasted image 20251019164312.png]]


Se nos abrirá el siguiente panel de configuración

![[Pasted image 20251019164356.png]]


Seleccionamos nuestros ficheros .CSV generados previamente

![[Pasted image 20251019164435.png]]


Los siguientes pasos de la configuración son a gusto propio, en este caso se ha dejado por defecto

![[Pasted image 20251019164524.png]]


Una vez personalizado nos debería de salir un gráfico similar a este

![[Pasted image 20251019164614.png]]

---


