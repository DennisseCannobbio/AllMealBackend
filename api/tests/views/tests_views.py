import json
from unittest.mock import patch, MagicMock
from django.urls import reverse
import pytest
from rest_framework import status
from rest_framework.test import APIClient
from api.models import Pedido, Menu, MenuResponse

#region Menus
class TestMenuViews:
    @pytest.fixture(autouse=True)
    def setup_method(self):
            self.client = APIClient()
            self.menu_id = 1
            
    @patch('api.models.Menu.objects.all')
    def test_get_menus(self, mock_all):
        """Test para obtener la lista de menús."""
        
        
        mock_menu_instance_1 = MagicMock(
            id=1,
            entrada='Ensalada de Tomate',
            plato_fondo='Arroz con pollo',
            postre='Helado',
            fecha='01-10-2024'
        )
        
        mock_menu_instance_2 = MagicMock(
            id=2,
            entrada='Ceviche Mixto',
            plato_fondo='Papafritas con pescado frito',
            postre='Mote con huesillo',
            fecha='01-10-2024'
        )
        
        mock_all.return_value = [mock_menu_instance_1, mock_menu_instance_2]

        response = self.client.get('/api/menus/')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['data']) == 2 
        assert response.data['data'][0]['entrada'] == 'Ensalada de Tomate'
        assert response.data['data'][1]['entrada'] == 'Ceviche Mixto'
        mock_all.assert_called()          
    
    @patch('api.models.Menu.objects.get')
    @patch('api.models.Menu.delete')
    def test_delete_menu(self, mock_delete, mock_get):
        """Test para eliminar un menú."""
        mock_menu_instance = MagicMock(id=self.menu_id)
        mock_get.return_value = mock_menu_instance

        url = f'/api/menus/{self.menu_id}'
        response = self.client.delete(url)
        assert response.status_code == status.HTTP_200_OK
        mock_get.assert_called_once_with(pk=self.menu_id)
        
    @patch('api.models.Menu.objects.get')
    def test_get_menu(self, mock_get):
        """Test para obtener un menú por pk."""
        mock_menu_instance = MagicMock(
            id=self.menu_id,
            entrada='Ensalada de Tomate',
            plato_fondo='Arroz con pollo',
            postre='Helado',
            fecha='01-10-2024'
        )
        mock_get.return_value = mock_menu_instance

        url = f'/api/menus/{self.menu_id}'
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['data']['entrada'] == 'Ensalada de Tomate'
        assert response.data['data']['plato_fondo'] == 'Arroz con pollo'
        mock_get.assert_called_once_with(pk=self.menu_id)

#endregion


#region Pedidos
## ! Aca implemente @pytest.mark.django_db para que acceda a la db, se que no es lo "correcto" para las pruebas unitarias, pero quería demostrarlo igualmente.
@pytest.mark.django_db
class TestPedidoViews:
    
        @pytest.fixture(autouse=True)
        def setup_method(self):
            self.client = APIClient()
            self.menu1 =  Menu.objects.create(entrada='Ensalada de Tomate', plato_fondo='Arroz con pollo', postre='Helado', fecha='01-10-2024') 
            self.menu2 = Menu.objects.create(entrada='Ceviche mixto', plato_fondo='Papas fritas con pescado frito', postre='Helado', fecha='01-10-2024') 
            self.pedido = Pedido.objects.create(nombre_cliente='Dennisse', fecha='01-10-2024')
            self.pedido.menus.set([self.menu1,self.menu2])
            
        def test_get_pedidos(self):
            """Test para obtener la lista de pedidos."""
            response = self.client.get('/api/pedidos/')
            assert response.status_code == status.HTTP_200_OK
            assert len(response.data['data']) == 1
            assert len(response.data['data'][0]['menus']) == 2
            assert response.data['data'][0]['menus'][0]['entrada'] == 'Ensalada de Tomate'
            assert response.data['data'][0]['menus'][0]['plato_fondo'] == 'Arroz con pollo'
            assert response.data['data'][0]['menus'][0]['postre'] == 'Helado'
            assert response.data['data'][0]['menus'][0]['fecha'] == '01-10-2024'
            
        def test_create_pedido(self):
            """Test para crear un nuevo pedido."""
            data = {
                'nombre_cliente': 'Alejandra',
                'fecha': '01-10-2024',
                'menus': [self.menu1.id, self.menu2.id]
            }
            url =  f'/api/pedidos/create'
            response = self.client.post(url, data, format='json')
            assert response.status_code == status.HTTP_200_OK
            assert response.data['data']['menus'] != []
            assert response.data['data']['menus'] == [1,2]
            
        def test_get_pedido(self):
            """Test para obtener un pedido por pk."""
            url = f'/api/pedidos/{self.pedido.id}'
            response = self.client.get(url, format='json')
            assert response.status_code == status.HTTP_200_OK
            assert response.data['data']['nombre_cliente'] == 'Dennisse'
            assert response.data['data']['menus'] != []
            assert response.data['data']['menus'] is not None
            assert response.data['data'] != {}
            assert response.data['data'] is not None
            
        def test_update_pedido(self):
            """Test para actualizar un pedido."""
            updated_data = {
                    "nombre_cliente": "Alejandra New",
                    "fecha": "02-10-2024",
                    "menus": [self.menu2.id]
            }
            url = f'/api/pedidos/{self.pedido.id}'
            response = self.client.put(url, updated_data, format='json')
            assert response.status_code == status.HTTP_200_OK
            assert response.data['Ok'] == True
            
        def test_delete_pedido(self):
            """Test para eliminar un pedido."""
            url = f'/api/pedidos/{self.pedido.id}'
            response = self.client.delete(url)
            assert response.status_code == status.HTTP_200_OK
            assert response.data['Ok'] == True
            assert Pedido.objects.filter(id=1).count() == 0
#endregion

#region Slack
class TestSlackViews:
    
    def setup_method(self):
        self.client = APIClient()
        
    @patch('requests.post')  
    @patch('api.models.Menu.objects.filter')  
    def test_send_menu_success(self, mock_filter, mock_post):
        """Test para enviar un menu a Slack."""
        mock_menu = MagicMock()
        mock_menu.id = 1
        mock_menu.fecha = '2024-10-02'
        mock_menu.entrada = 'Ensalada'
        mock_menu.plato_fondo = 'Pollo al horno'
        mock_menu.postre = 'Helado'
        
        mock_queryset = MagicMock()
        mock_queryset.exists.return_value = True  
        mock_queryset.__iter__.return_value = [mock_menu]  
        
        mock_filter.return_value = mock_queryset  

        mock_post.return_value.status_code = 200 
        
        url = f'/api/slack/sendmenu'
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['Ok'] is True
        assert response.data['status'] == "success"
        assert response.data['message'] == "Menú enviado exitosamente"
        assert mock_post.called  

    @patch('requests.post')  
    @patch('api.models.Menu.objects.filter')
    def test_send_menu_error(self, mock_filter, mock_post):
        """Test para enviar un menu a Slack y que ocurra un error de no existen menus."""
        mock_filter.return_value.exists.return_value = False
        
        url = f'/api/slack/sendmenu'
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['Ok'] is False
        assert response.data['status'] == "error"
        assert "No existen menús" in response.data['message']
        assert not mock_post.called  

    
    @patch('requests.post')
    def test_receive_response_with_challenge(self, mock_post):
        """Test para recibir la prueba desde slack de conexion (desde slack envia un challenge)."""
        url = '/api/slack/response'
        response = self.client.post(url, {'challenge': 'test_challenge'})
        assert response.status_code == status.HTTP_200_OK
        assert response.data == {'challenge': 'test_challenge'}
        
    @patch('requests.post')
    @patch('api.models.Menu.objects.get') 
    @patch('api.models.MenuResponse')
    def test_receive_response_no_menus(self, mock_menu_response, mock_menu_get, mock_post):
        mock_menu_get.side_effect = Menu.DoesNotExist  

        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"ok": True, "text": "Mensaje enviado."} 

        payload = {
            'payload': json.dumps({
                'type': 'block_actions',
                'user': {'id': 'U12345'},
                'actions': [{'value': '1'}]  
            })
        }

        url = '/api/slack/response'  
        response = self.client.post(url, payload, format='json')  

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data == {'text': 'No se encontró el menú con ID 1.'}



    @patch('requests.post')
    @patch('api.models.Menu.objects.get')  
    @patch('api.models.MenuResponse.objects.create')  
    def test_receive_response_valid_payload(self,mock_create, mock_menu_get, mock_post):

        mock_menu_instance = MagicMock()
        mock_menu_instance.entrada = 'Ensalada'
        mock_menu_instance.plato_fondo = 'Pollo al horno'
        mock_menu_instance.postre = 'Flan'
        
        mock_menu_get.return_value = mock_menu_instance  

        mock_post.return_value.status_code = 200  
        mock_post.return_value.json.return_value = {"ok": True, "text": "Mensaje enviado."}  

        payload = {
            'payload': json.dumps({
                'type': 'block_actions',
                'user': {'id': 'U12345'},
                'actions': [{'value': '1'}]  
            })
        }

        url = '/api/slack/response'  
        response = self.client.post(url, payload, format='json') 

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {"text": "Mensaje enviado a Slack y guardado en db!."}

        mock_create.assert_called_once_with(
            user_id='U12345',
            response_text='Menú N°1 seleccionado',
            menu_id=1
        )



#endregion