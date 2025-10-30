Hacemos un update.

```bash
┌──(kali㉿kali)-[~]
└─$ sudo apt update 
```

Instalamos gofish

```bash
┌──(kali㉿kali)-[~]
└─$ sudo apt install gofish
```

Ejecutamos el programa (La primera vez que lo hagamos nos dará una contraseña temporal, nos la hará cambiar)

```bash
┌──(kali㉿kali)-[~]
└─$ sudo gophish /h                           
Starting gophish...
Opening Web UI https://127.0.0.1:3333
```

Ahora instalaremos go

```bash
┌──(kali㉿kali)-[~]
└─$ sudo apt-get -y install golang-go 
```

Instalamos git también si no lo tenemos

```bash
┌──(kali㉿kali)-[~]
└─$ sudo apt-get install git                    
```

Instalamos Mailhog

```bash
┌──(kali㉿kali)-[~]
└─$ go install github.com/mailhog/MailHog@latest
```

Iniciamos Mailhog y lo dejamos ahí por el momento

```bash
┌──(kali㉿kali)-[~]
└─$ ~/go/bin/MailHog
```

Ahora en la pagina web de gophish lo primero será crear un "Sending Profile", estos son las configuraciones que hay que poner:
- Nombre: Ivan - Sending Profile
- SMTP From: mailhog@test.com
- Host: 127.0.0.1:1025
- Ignorar errores de certificados: activada

Ahora vamos a grupos y ponemos un email, no le va a llegar es solo para que no nos de error en un paso siguiente.

Hacemos un email template mediante html:

```html
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Notificación de Seguridad</title>
</head>
<body>
    <p>Estimado/a {{.FirstName}} {{.LastName}},</p>
    <p>
        Hemos detectado actividad inusual en su cuenta. Para garantizar su seguridad, le solicitamos que verifique su cuenta de inmediato.
    </p>
    <p>
        Por favor, haga clic en el siguiente enlace para iniciar sesión y verificar su información:
    </p>
    <p>
        <a href="{{.URL}}" target="_blank">Verificar Cuenta</a>
    </p>
    <p>
        Si no reconoce esta actividad, por favor contacte a nuestro soporte técnico inmediatamente.
    </p>
    <p>Saludos cordiales,</p>
    <p>Equipo de Seguridad</p>
{{.Tracker}}</body>
</html>
```

También creamos una landing page, además tendremos que activar las siguientes opciones:
- Capture Submitted Data
- Capture Passwords

Ahora vamos a campañas creamos una, ponemos un nombre, en URL: ponemos `http://localhost/` el resto es seleccionar lo que hemos ido haciendo, le damos a lanzar campaña y vemos desde el mailhog que ha llegado el correo que hemos creado antes.

```email
From 	mailhog@test.com
Subject 	Testeando
To 	"i f" <ivan.fernandezaguilera@tajamar365.com> 

Estimado/a i f,

Hemos detectado actividad inusual en su cuenta. Para garantizar su seguridad, le solicitamos que verifique su cuenta de inmediato.

Por favor, haga clic en el siguiente enlace para iniciar sesión y verificar su información:

Verificar Cuenta

Si no reconoce esta actividad, por favor contacte a nuestro soporte técnico inmediatamente.

Saludos cordiales,

Equipo de Seguridad
```



