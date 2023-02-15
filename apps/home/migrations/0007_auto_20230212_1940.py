# Generated by Django 3.2.16 on 2023-02-12 22:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0006_alter_cad_cliente_model_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cad_cliente_model',
            name='honorarios',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name=''),
        ),
        migrations.AlterField(
            model_name='cad_cliente_model',
            name='nao',
            field=models.IntegerField(blank=True, null=True, verbose_name=''),
        ),
        migrations.AlterField(
            model_name='cad_cliente_model',
            name='operacional',
            field=models.IntegerField(blank=True, null=True, verbose_name=''),
        ),
        migrations.AlterField(
            model_name='cad_cliente_model',
            name='sim',
            field=models.IntegerField(blank=True, null=True, verbose_name=''),
        ),
        migrations.AlterField(
            model_name='cad_cliente_model',
            name='tcc',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name=''),
        ),
    ]