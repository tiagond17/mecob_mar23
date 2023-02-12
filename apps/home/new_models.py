# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models

class CadClientesInputs(models.Model):
    taxas = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)
    sim = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)
    nao = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)
    operacional = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)
    tcc = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)
    honorarios = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)
    animal = models.CharField(max_length=128, blank=True, null=True)
    evento = models.CharField(max_length=128, blank=True, null=True)
    informar_repasse = models.CharField(max_length=128, blank=True, null=True)
    vl_juros = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)
    vl_boletos = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)
    vl_pago = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)
    deposito = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)
    repasse = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'cad_clientes_inputs'


class CadClientesOficial(models.Model):
    taxas = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)
    sim = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)
    nao = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)
    operacional = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)
    tcc = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)
    honorarios = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)
    animal = models.CharField(max_length=128, blank=True, null=True)
    evento = models.CharField(max_length=128, blank=True, null=True)
    informar_repasse = models.CharField(max_length=128, blank=True, null=True)
    vl_juros = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)
    vl_boletos = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)
    vl_pago = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)
    deposito = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)
    repasse = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)
    nome_vendedor = models.CharField(max_length=16)
    id_vendedor = models.CharField(max_length=2)

    class Meta:
        managed = False
        db_table = 'cad_clientes_oficial'