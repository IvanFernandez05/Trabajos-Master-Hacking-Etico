#### Instalación de Elasticsearch, Kibana y Elastic Agent

Descargamos la clave pública GPG usada por Elastic para firmar sus paquetes, luego la guardamos permitiendo que APT confíe en los paquetes que han sido firmados por Elastic.

```bash
┌──(ivan㉿kali)-[~]
└─$ wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo gpg --no-default-keyring --keyring gnupg-ring:/etc/apt/trusted.gpg.d/elasticsearch.gpg --import

[sudo] contraseña para ivan: 
gpg: anillo '/etc/apt/trusted.gpg.d/elasticsearch.gpg' creado
gpg: creado el directorio '/root/.gnupg'
gpg: /root/.gnupg/trustdb.gpg: se ha creado base de datos de confianza
gpg: clave D27D666CD88E42B4: clave pública "Elasticsearch (Elasticsearch Signing Key) <dev_ops@elasticsearch.org>" importada
gpg: Cantidad total procesada: 1
gpg:               importadas: 1
```

Damos los permisos necesarios

``` bash
┌──(ivan㉿kali)-[~]
└─$ sudo chmod 644 /etc/apt/trusted.gpg.d/elasticsearch.gpg
```

Añadimos el repositorio de "Elastic Search" a nuestra lista de fuentes.

``` bash
──(ivan㉿kali)-[~]
└─$ echo "deb https://artifacts.elastic.co/packages/7.x/apt stable main" | sudo tee -a /etc/apt/sources.list.d/elastic-7.x.list
deb https://artifacts.elastic.co/packages/7.x/apt stable main
                                                             
┌──(ivan㉿kali)-[~]
└─$ sudo apt update
```

Instalamos "Elastic Search" y "Kibana"

```bash
┌──(ivan㉿kali)-[~]
└─$ sudo apt install elasticsearch
 
┌──(ivan㉿kali)-[~]
└─$ sudo apt install kibana 
```

Editamos el archivo de configuración de elasticsearch con las siguientes configuraciones (/etc/elasticsearch/elasticsearch.yml)

```bash
#Cambiamos el nombre del cluster  
cluster.name: ivan-elk  
#Definimos un nombre para este nodo  
node.name: elk-1 
#Cambiamos la configuración de red  
network.host: 0.0.0.0  
#Configuramos discovery.type como nodo único.  
discovery.type: single-node
#Debajo del apartado de security incluiremos estas dos lineas que seran imprescindibles para instalar "Elastic Agent"
xpack.security.enabled: true
xpack.security.authc.api_key.enabled: true
```

Reiniciamos el servicio

```bash
┌──(ivan㉿kali)-[~]
└─$ sudo service elasticsearch start 
```

Comprobamos viendo el estado del servicio

``` bash
┌──(ivan㉿kali)-[~]
└─$ sudo service elasticsearch status
● elasticsearch.service - Elasticsearch
     Loaded: loaded (/usr/lib/systemd/system/elasticsearch.service; disabled; preset: disabled)
     Active: active (running) since Fri 2025-10-10 07:23:41 EDT; 45s ago
```

Con este comando generaremos contraseñas vara diferentes usuarios de kibana

```bash
┌──(ivan㉿kali)-[~]
└─$ sudo /usr/share/elasticsearch/bin/elasticsearch-setup-passwords interactive         
Initiating the setup of passwords for reserved users elastic,apm_system,kibana,kibana_system,logstash_system,beats_system,remote_monitoring_user.
You will be prompted to enter passwords as the process progresses.
Please confirm that you would like to continue [y/N]y
Enter password for [elastic]: 
Reenter password for [elastic]: 
Enter password for [apm_system]: 
Reenter password for [apm_system]: 
Enter password for [kibana_system]: 
Reenter password for [kibana_system]: 
Enter password for [logstash_system]: 
Reenter password for [logstash_system]: 
Enter password for [beats_system]: 
Reenter password for [beats_system]: 
Enter password for [remote_monitoring_user]: 
Reenter password for [remote_monitoring_user]: 
Changed password for user [apm_system]
Changed password for user [kibana_system]
Changed password for user [kibana]
Changed password for user [logstash_system]
Changed password for user [beats_system]
Changed password for user [remote_monitoring_user]
Changed password for user [elastic]
```

Ahora editaremos el archivo de configuración de kibana (/etc/kibana/kibana.yml)

```bash
#Descomentamos server.port 
server.port: 5601
#Cambiamos server.host 
server.host: "0.0.0.0"  
#Cambiamos el server.name  
server.name: "ivan-kibana"   
#Descomentamos elasticsearch.host  
elasticsearch.hosts: ["http://localhost:9200"]
#Cambiamos la contraseña que viene por la que hemos puesto
elasticsearch.username: "kibana_system"
elasticsearch.password: "Contra123"
```

Reiniciamos y comprobamos el estado.

```bash
┌──(ivan㉿kali)-[~]
└─$ sudo service kibana start                                                                                                                                          
┌──(ivan㉿kali)-[~]
└─$ sudo service kibana status                                                                  
● kibana.service - Kibana
     Loaded: loaded (/etc/systemd/system/kibana.service; disabled; preset: disabled)
     Active: active (running) since Fri 2025-10-10 07:33:56 EDT; 14s ago
```

Entramos mediante la siguiente ruta: "[http://localhost:5601](http://localhost:5601/) y entra en la pagina de elastic, poniendo usuario ("elastic" que es el admin) y contraseña.

| Usuario         | Rol           | Uso                                                                                           |
| --------------- | ------------- | --------------------------------------------------------------------------------------------- |
| `elastic`       | superuser     | Administrador total del cluster                                                               |
| `kibana_system` | kibana_system | Usuario interno que Kibana usa para conectarse a Elasticsearch (no para login en la interfaz) |

``` bash
┌──(ivan㉿kali)-[/etc]
└─$ curl -I http://localhost:5601
HTTP/1.1 302 Found
location: /login?next=%2F
x-content-type-options: nosniff
referrer-policy: no-referrer-when-downgrade
content-security-policy: script-src 'unsafe-eval' 'self'; worker-src blob: 'self'; style-src 'unsafe-inline' 'self'
kbn-name: ivan-kibana
kbn-license-sig: 9b83cb2fcd7abc70cd733f8f11067997d1d68079584cb65234659ff73f933e5a
cache-control: private, no-cache, no-store, must-revalidate
content-length: 0
Date: Sat, 11 Oct 2025 10:54:22 GMT
Connection: keep-alive
Keep-Alive: timeout=120
```

Estando en la página principal "home", le damos a "Add integrations", habrá muchas categorías nosotros buscaremos "Elastic Stack" y añadiremos Elastic Agent, nos pedirá un nombre y ya estaría integrado. 

#### Configuración del agente para recopilar datos de seguridad del host

Ahora queremos recopilar datos del host, lo primero que hay que hacer es instalar Elastic Agent en nuestra maquina desde esta [página](https://www.elastic.co/downloads/past-releases/elastic-agent-7-17-29).

``` bash
┌──(ivan㉿kali)-[~/Downloads]
└─$ tar xzvf elastic-agent-7.17.29-linux-x86_64.tar.gz
```

Editamos el archivo "elastic-agent.yml"

```bash
┌──(ivan㉿kali)-[~/Downloads/elastic-agent-7.17.29-linux-x86_64]
└─$ nano elastic-agent.yml
```

Y habrá que dejar el apartado "outputs" de esta manera

```bash
outputs:  
  default:
    type: elasticsearch
    hosts: 
      - 'http://localhost:9200'
    api_key: "example-key"
    username: elastic
    password: Contra123
```

Ejecutamos este comando para instalar el agente

``` bash
┌──(ivan㉿kali)-[~/Downloads/elastic-agent-7.17.29-linux-x86_64]
└─$ sudo ./elastic-agent install                                                             
[sudo] password for ivan: 
Elastic Agent will be installed at /opt/Elastic/Agent and will run as a service. Do you want to continue? [Y/n]:y
Do you want to enroll this Agent into Fleet? [Y/n]:n
Elastic Agent has been successfully installed.
```

Ahora si vamos a http://localhost:5601/app/security/  vemos donde Elastic centraliza los datos de seguridad del host.
