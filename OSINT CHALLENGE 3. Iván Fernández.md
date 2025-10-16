##### Task 1: What is the originating website? 

www.roserestaurant.com

##### Task 2: What is the possible administrator password? 

WK7JNgYcDkzac

##### Task 3: How is it possible to obtain information from OSINT methods? 

Los motores de búsqueda tienen la capacidad de indexar datos públicos, como archivos, listados y copias en caché, esto significa que mucha información sensible puede quedar al alcance de cualquiera a través de datos que los robots de búsqueda rastrean. Con las cadenas de búsqueda adecuadas, es posible localizar esta información.

##### Task 4: What are the google dorks to be used to uncover relevant information? 

- site:
- "Index of"
- intext:
- intitle:

##### Task 5: Can you use the obtained password to further investigate the problem? 

No sin la autorización del propietario del sitio web, en caso de tenerla si.

##### Task 6: Where is the administrator password located? (In the _vti_private folder, service.pwd file) 

En la carpeta  "/vti_pvt/", y el archivo se llama "service.pwd"

##### Task 7: What functionality allows the attacker to simply uncover the administrator password? 

La funcionalidad de "Index of" del servidor web permite mostrar directorios públicos de archivos.

##### Task 8: How could you possibly remediate this issue?

- Desactivar el listado de directorios "Index of" si no es realmente necesario. 
- Asegurarte de eliminar o mover cualquier archivo sensible fuera del árbol que sea accesible al público. 
- Es fundamental configurar los permisos adecuados en el sistema de archivos (nada de permitir lectura para todos). 
- No olvidar proteger las carpetas administrativas con autenticación y HTTPS. 
- Revisar los registros y busca accesos automatizados; notifica al propietario y asegúrate de parchear cualquier vulnerabilidad.