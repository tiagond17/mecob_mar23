# Generated by Django 3.2.16 on 2023-03-01 21:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0008_debito_descricao'),
    ]

    operations = [
        migrations.AddField(
            model_name='credito',
            name='descricao',
            field=models.CharField(blank=True, max_length=128, null=True, verbose_name=''),
        ),
    ]