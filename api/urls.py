from django.urls import path
from .views import get_menus, create_menu, menu_detail, create_user, user_detail,get_users, get_pedidos,create_pedido, pedido_detail, send_menu, receive_response, get_responses

urlpatterns = [
    #** Menu
    path('menus/', get_menus, name='get_menus'),
    path('menus/create', create_menu, name='create_menu'),
    path('menus/<int:pk>', menu_detail, name='menu_detail'),
    # ** Users
    path('users/', get_users, name='get_users'),
    path('users/create', create_user, name='create_user'),
    path('users/<int:pk>', user_detail, name='user_detail'),
    # ** Pedidos
    path('pedidos/', get_pedidos, name='get_pedidos' ),
    path('pedidos/create', create_pedido,name='create_pedido' ),
    path('pedidos/<int:pk>', pedido_detail,name='pedido_detail' ),
    # ** Slack
    path('slack/sendmenu', send_menu, name='get_slack'),
    path('slack/response', receive_response, name='receive_response' ),
    path('slack/get_responses', get_responses, name='get_responses' )
    
    
    
]