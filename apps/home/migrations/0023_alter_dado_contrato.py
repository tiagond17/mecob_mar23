# Generated by Django 3.2.16 on 2023-02-16 23:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0022_alter_dado_evento'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dado',
            name='contrato',
            field=models.CharField(blank=True, max_length=128, null=True, verbose_name=''),
        ),
    ]