# Generated by Django 3.2.16 on 2023-02-16 23:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0020_dado'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dado',
            name='deposito',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name=''),
        ),
        migrations.AlterField(
            model_name='dado',
            name='nu_parcela',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name=''),
        ),
    ]