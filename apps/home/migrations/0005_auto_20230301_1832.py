# Generated by Django 3.2.16 on 2023-03-01 21:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0004_taxa'),
    ]

    operations = [
        migrations.CreateModel(
            name='Credito',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name': 'credito',
                'verbose_name_plural': 'creditos',
            },
        ),
        migrations.AddField(
            model_name='taxa',
            name='taxas',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, verbose_name=''),
        ),
        migrations.AlterField(
            model_name='taxa',
            name='cliente',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='home.pessoas'),
        ),
    ]