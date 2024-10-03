# api_all_meal

Este proyecto fue realizado con Python y django (django-rest-framework), es una API para gestionar el sistema AllMeal.

Ejecute los siguientes pasos para ejecutar el proyecto en un entorno local:

## Instalación

1. Debe tener instalado python en su equipo local. 

1. Clonar el repositorio en su carpeta:
   
         git clone https://github.com/DennisseCannobbio/AllMealBackend.git
   
2. Crear y activar su entorno virtual:

        python -m venv venv
        source venv/bin/activate (En linux y mac)
        venv\Scripts\activate (En windows)
   
3. Instale las dependencias necesarias:
   
        pip install -r requirements.txt

4. Necesita configurar las variables de entorno:
   
        cp .env.example .env (Debe rellenar con sus credenciales correspondientes)

5. Para rellenar las credenciales de variables de entorno, necesita tener su channel-id de Slack, su Webhook de Slack y ruta publica que será usada para los eventos e interacciones del bot en slack (en este caso yo utilice ngrok), a continuación, un ejemplo de cómo debería estar el archivo .env:
   
         SLACK_WEBHOOK =https://my-slack-webhook.com/services/ABCD/ABCD
         CHANNEL_NAME ="test-all-meal"
         NGROK_URL=https://my-ngrok-route.ngrok-free.app
         
7. Si usted utilizará ngrok igualmente, debe descargarlo de la página oficial (https://ngrok.com/download)
8. Debe descargar el .ZIP en su equipo y descomprimirlo.
9. Luego ejecute el archivo ngrok.exe, se abrirá una pantalla CMD y le pedirá que ingrese a su cuenta, por favor ingrese.
10. Finalmente cuando este logueado en su cuenta, ejecute el comando:
    
        ngrok.exe http 8000

11. Este comando dejará su IP pública temporalmente, debe copiar la ruta de Forwarding en el archivo .env donde dice NGROK_URL= incluido el https (Ej: NGROK_URL=https://miruta).
12. Luego de tener todas las variables de entorno necesarias, debe ejecutar las migraciones correspondientes con los siguientes comandos:

        python manage.py makemigrations
        python manage.py migrate

13. Finalmente ejecute el servidor

        python manage.py runserver

## Pruebas
1. Para las pruebas debe estar dentro de la carpeta del proyecto, activar su entorno virtual
   
           python -m venv venv
           source venv/bin/activate (En linux y mac)
           venv\Scripts\activate (En windows)
   
3. Ejecutar el comando:

            pytest api/tests/views/test_views.py
