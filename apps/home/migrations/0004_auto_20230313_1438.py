# Generated by Django 3.2.16 on 2023-03-13 17:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0003_alter_perfil_options'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cadcliente',
            name='deposito',
        ),
        migrations.RemoveField(
            model_name='cadcliente',
            name='nome',
        ),
        migrations.RemoveField(
            model_name='cadcliente',
            name='repasse',
        ),
        migrations.RemoveField(
            model_name='cadcliente',
            name='vl_boletos',
        ),
        migrations.RemoveField(
            model_name='cadcliente',
            name='vl_juros',
        ),
        migrations.RemoveField(
            model_name='cadcliente',
            name='vl_pago',
        ),
    ]
