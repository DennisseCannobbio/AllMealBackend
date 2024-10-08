# Generated by Django 5.1.1 on 2024-10-03 14:59

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Menu',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('entrada', models.CharField(max_length=100)),
                ('plato_fondo', models.CharField(max_length=100)),
                ('postre', models.CharField(max_length=100)),
                ('fecha', models.CharField(max_length=12)),
            ],
        ),
        migrations.CreateModel(
            name='MenuResponse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('response_text', models.TextField()),
                ('user_id', models.CharField(max_length=255)),
                ('menu_id', models.IntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Pedido',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.CharField(max_length=12)),
                ('nombre_cliente', models.CharField(max_length=100)),
                ('menus', models.ManyToManyField(related_name='pedidos', to='api.menu')),
            ],
        ),
        migrations.CreateModel(
            name='Usuario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('usuario', models.CharField(max_length=100)),
                ('contraseña', models.CharField(max_length=15)),
                ('pedidos', models.ManyToManyField(blank=True, to='api.pedido')),
            ],
        ),
    ]
