# Generated by Django 3.2.16 on 2023-03-18 18:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0009_alter_dado_contrato'),
    ]

    operations = [
        migrations.AddField(
            model_name='dado',
            name='id_excel',
            field=models.IntegerField(blank=True, null=True, verbose_name=''),
        ),
    ]