# Generated by Django 3.2.16 on 2023-03-18 18:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0013_auto_20230318_1525'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dado',
            name='contrato',
            field=models.CharField(blank=True, max_length=512, null=True, verbose_name=''),
        ),
    ]
