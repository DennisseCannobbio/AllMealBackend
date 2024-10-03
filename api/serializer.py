from rest_framework import serializers
from .models import Menu, Usuario, Pedido, MenuResponse

class MenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = '__all__'

class PedidoSerializer(serializers.ModelSerializer):
    
    menus = MenuSerializer(many=True)

    class Meta:
        model = Pedido
        fields = '__all__'
        
class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = '__all__'
        

class PedidoCreateUpdateSerializer(serializers.ModelSerializer,):
    
    menus = serializers.PrimaryKeyRelatedField(queryset=Menu.objects.all(), many=True)
    
    class Meta:
        model = Pedido
        fields = ['nombre_cliente', 'menus', 'fecha']
        
    def update(self, instance, validated_data):
        
        instance.nombre_cliente = validated_data.get('nombre_cliente', instance.nombre_cliente)
        
        instance.fecha = validated_data.get('fecha', instance.fecha)

        new_menus = validated_data.get('menus', [])
        
        instance.menus.set(new_menus)  
        
        instance.save()
        
        return instance

class MenuResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuResponse
        fields = [ 'user_id', 'menu_id', 'created_at', 'response_text']  