from datetime import date
import json
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from slack_sdk import WebClient
from .models import Menu, MenuResponse, Usuario, Pedido
from .serializer import MenuSerializer, UsuarioSerializer, PedidoSerializer,PedidoCreateUpdateSerializer, MenuResponseSerializer
import os
from pathlib import Path
from dotenv import load_dotenv
from slack_sdk.errors import SlackApiError
import requests
from django.db import transaction

load_dotenv()
# key = os.environ.get('SLACK_TOKEN')
SLACK_WEBHOOK = os.environ.get('SLACK_WEBHOOK')

# region Menu
@api_view(['GET'])
def get_menus(request):
    menus = Menu.objects.all()
    serializer = MenuSerializer(menus, many=True)
    return Response({"Ok": True, "status": "success", "data": serializer.data})

@api_view(['POST'])
def create_menu(request):
    serializer = MenuSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"Ok": True,"status": "success", "data": serializer.data }, status=status.HTTP_200_OK)
    else:
        return Response({"Ok": False,"status": "error", "message": serializer.errors }, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET', 'PUT', 'DELETE'])
def menu_detail(request, pk):
    try:
        menu = Menu.objects.get(pk=pk)
    except:
        return Response({"Ok": False,"status": "error", "message": "Ups!, the menu does not exists on the database"}, status=status.HTTP_404_NOT_FOUND)
    
    
    match request.method:
        case 'GET':
            serializer = MenuSerializer(menu)
            return Response({"Ok": True,"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)

        case 'PUT':
            print("Entrando a la vista de actualización del menú")
            serializer = MenuSerializer(menu, data=request.data)
            print("despues del serializer")
            
            
            if serializer.is_valid():
                print("preguntando si es valido")
                print(request.data)
                serializer.save()
                print("Retornando OK True")
                return  Response({"Ok": True,"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
            else:
                print("Retornando OK False")
                
                return Response({"Ok": False,"status": "error", "message": "Ups!, an error has ocurred updating the menu"}, status=status.HTTP_404_NOT_FOUND)
        
        case 'DELETE':
            menu.delete()
            return Response({"Ok": True,"status": "success"}, status=status.HTTP_200_OK)
            
# endregion

# region Pedidos
@api_view(['GET'])
def get_pedidos(request):
    pedidos = Pedido.objects.all()
    serializer = PedidoSerializer(pedidos, many=True)
    return Response({"Ok": True, "status": "success", "data": serializer.data})

@api_view(['POST'])
def create_pedido(request):
    serializer = PedidoCreateUpdateSerializer(data=request.data)
    print(serializer, 'linea 59')
    
    if serializer.is_valid():
        serializer.save()
        return Response({"Ok": True,"status": "success", "data": serializer.data }, status=status.HTTP_200_OK)
    else:
        return Response({"Ok": False,"status": "error", "message": serializer.errors }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def pedido_detail(request, pk):
    try:
        pedido = Pedido.objects.get(pk=pk)
    except:
        return Response({"Ok": False,"status": "error", "message": "Ups!, the order does not exists on the database"}, status=status.HTTP_404_NOT_FOUND)

    match request.method:
        case 'GET':
            serializer = PedidoCreateUpdateSerializer(pedido)
            return Response({"Ok": True,"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)

        case 'PUT':
            serializer = PedidoCreateUpdateSerializer(pedido, data=request.data)
            
            if serializer.is_valid():
                # pedido.menus.set(menus)
                serializer.save()
                return  Response({"Ok": True,"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({"Ok": False,"status": "error", "message": "Ups!, an error has ocurred updating the order", "error": serializer.errors}, status=status.HTTP_404_NOT_FOUND)
        case 'DELETE':
            pedido.delete()
            return Response({"Ok": True,"status": "success"}, status=status.HTTP_200_OK)
# endregion

#region Slack
## ! En esta parte deje una peticion get para enviar el menu manualmente => Es para motivos de pruebas.
@api_view(['GET'])
def send_menu(request):
        webhook_url = SLACK_WEBHOOK
        
        today = date.today().strftime('%d-%m-%Y')
        menus = Menu.objects.filter(fecha=today)
        
        ok = False
        status = "error"
        message = f"No existen menús, por favor agregue los del día de hoy ({today})"  

        blocks = []
        if menus.exists():
            for menu in menus:
                menu_block = {
                                "type": "section",
                                "text": {
                                    "type": "mrkdwn",
                                    "text": f"*Menú del día N° {menu.id} ({menu.fecha}):*\n" \
                                            f"Entrada: {menu.entrada}\n" \
                                            f"Plato de Fondo: {menu.plato_fondo}\n" \
                                            f"Postre: {menu.postre}"
                                },
                                "accessory": {
                                    "type": "button",
                                    "text": {
                                        "type": "plain_text",
                                        "text": f"Elegir Menú N° {menu.id}"
                                    },
                                    "value": str(menu.id), 
                                    "action_id": "menu_selection"
                                }
                            }
                
                blocks.append(menu_block)
                
            slack_data = {
                "blocks": blocks
            }
                
            try:
                response = requests.post(webhook_url, json=slack_data)
                print(response, 'response aca 149')
                message = "Menú enviado exitosamente"
                ok = True
                status = "success"
                print(message)
                    
            except:
                message = f"Error al enviar el menú"
                ok = False
                status = "error"
                print(message)
                    
        else:
            message = message
            ok = False
            status = "error"
            print(message)
        
        return Response({"Ok": ok,"status": status, "message": message})


## ! En esta parte recibimos la respuesta luego que le enviamos el menu al usuario. Nos retornará el menu correspondiente y lo guardará en la db.
@api_view(['POST'])
def receive_response(request):
    
    if 'challenge' in request.data:
        return Response({'challenge': request.data['challenge']}, status=status.HTTP_200_OK)
    
    slack_data = {
        "text": ''
    }
    
    try:
        if 'payload' in request.data:
            payload_str = request.data['payload']
            
            payload = json.loads(payload_str)
            
            if payload.get('type') == 'block_actions':
                user_id = payload['user']['id']  
                action_value  = payload['actions'][0]['value'] 

                try:
                    menu_id = int(action_value)
                    menu = Menu.objects.get(id=menu_id)
                    
                    response_message = (
                        f"¡Claro! Aquí tienes el Menú del día N°{menu_id}:\n\n"
                        f"Entrada: {menu.entrada}\n"
                        f"Plato de Fondo: {menu.plato_fondo}\n"
                        f"Postre: {menu.postre}\n\n"
                        "Se guardará su pedido."
                    )

                    webhook_url = SLACK_WEBHOOK 
                    
                    slack_data = {
                        "text": response_message
                    }
                    
                    try:
                        response = requests.post(webhook_url, json=slack_data)
                        
                        if response.status_code == 200:
                            print(response.status_code, 'status code resp')
                            MenuResponse.objects.create(
                                user_id=user_id,
                                response_text=f"Menú N°{menu_id} seleccionado",
                                menu_id=menu_id
                            )
                            print("paso creacion :D")
                            return Response({"text": "Mensaje enviado a Slack y guardado en db!."}, status=status.HTTP_200_OK)
                        else:
                            return Response({"text": "Error al enviar mensaje a Slack."}, status=response.status_code)
                        
                    except Exception as e:
                        print(e)
                        return Response({"text": "Ups! Ha ocurrido un error al enviar a Slack."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                except Menu.DoesNotExist:
                    return Response({"text": f"No se encontró el menú con ID {menu_id}."}, status=status.HTTP_404_NOT_FOUND)
                
        return Response({"text": "OK"}, status=status.HTTP_200_OK)
    except Exception as e:
        print(e, 'aca 242')
        return Response({"text": "Error"}, status=status.HTTP_400_BAD_REQUEST)
        



## ! Aca retornamos toda la data que hemos guardado de los usuarios via slack, que solicitan un menu.
@api_view(['GET'])
def get_responses(request):
    data = MenuResponse.objects.all()
    serializer = MenuResponseSerializer(data, many=True)
    return Response({"Ok": True,"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
    
# region Users
@api_view(['GET'])
def get_users(request):
    users = Usuario.objects.all()
    serializer = UsuarioSerializer(users, many=True)
    return Response({"Ok": True,"status": "success", "data": serializer.data})

@api_view(['POST'])
def create_user(request):
    serializer = UsuarioSerializer(data=request.data)
    
    if serializer.is_valid():
        serializer.save()
        return Response({"Ok": True, "status": "success", "data": serializer.data }, status=status.HTTP_200_OK)
    else:
        return Response({"Ok": False, "status": "error", "message": serializer.errors }, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET', 'PUT', 'DELETE'])
def user_detail(request, pk):
    try:
        user = Usuario.objects.get(pk=pk)
    except:
        return Response({"Ok": False,"status": "error", "message": "Ups!, the user does not exists on the database"}, status=status.HTTP_404_NOT_FOUND)
    
    
    match request.method:
        case 'GET':
            serializer = UsuarioSerializer(user)
            return Response({"Ok": True, "status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
        case 'PUT':
            serializer = UsuarioSerializer(user, data=request.data)
            
            if serializer.is_valid():
                serializer.save()
                return  Response({"Ok": True, "status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({"Ok": False,"status": "error", "message": "Ups!, an error has ocurred updating the menu"}, status=status.HTTP_404_NOT_FOUND)
        case 'DELETE':
            user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

#endregion