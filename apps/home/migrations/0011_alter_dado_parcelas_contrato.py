# Generated by Django 3.2.16 on 2023-03-18 18:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0010_dado_id_excel'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dado',
            name='parcelas_contrato',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name=''),
        ),
    ]