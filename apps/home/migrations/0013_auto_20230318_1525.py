# Generated by Django 3.2.16 on 2023-03-18 18:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0012_auto_20230318_1523'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dado',
            name='contrato',
            field=models.CharField(blank=True, max_length=300, null=True, verbose_name=''),
        ),
        migrations.AlterField(
            model_name='dado',
            name='id_contrato',
            field=models.CharField(blank=True, max_length=128, null=True, verbose_name=''),
        ),
    ]
