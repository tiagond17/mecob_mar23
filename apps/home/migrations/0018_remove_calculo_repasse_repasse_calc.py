# Generated by Django 3.2.16 on 2023-02-16 18:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0017_calculo_repasse_repasse_calc'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='calculo_repasse',
            name='repasse_calc',
        ),
    ]