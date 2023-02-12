# -*- encoding: utf-8 -*-

from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
"""
Copyright (c) 2019 - present AppSeed.us
"""
#TODO:  selecionar o que vendedo e totalizar quanto ele tem para recebe entre agosto/22
from . import existing_models
#*pegar o id e nome do vendedor e colocar no cad cliente
class CAD_Cliente_Model(models.Model):
    #!Talvez remover os campos nome e codigo caso encontre a referencia deles
    vendedor = models.ForeignKey('Pessoas', on_delete=models.CASCADE, blank=True, null=True)
    nome = models.CharField(_(""), max_length=128, blank=True, null=True)
    codigo = models.IntegerField(_(""), blank=True, null=True)
    
    #* Todos os campos abaixo estão corretas
    taxas = models.DecimalField(_("Taxas"), max_digits=5, decimal_places=2, blank=True, null=True)
    sim = models.IntegerField(_(""), default=3/100, blank=True, null=True)
    nao = models.IntegerField(_(""), default=20/100, blank=True, null=True)
    operacional = models.IntegerField(_(""), default=5/100, blank=True, null=True)
    tcc = models.DecimalField(_(""), max_digits=5, decimal_places=2, default=1/100, blank=True, null=True)
    honorarios = models.DecimalField(_(""), max_digits=5, decimal_places=2, default=3/100, blank=True, null=True)
    animal = models.CharField(_(""), max_length=256, blank=True, null=True)
    evento = models.CharField(_(""), max_length=256, blank=True, null=True)
    informar_repasse = models.CharField(_(""), max_length=50, blank=True, null=True)
    vl_juros = models.DecimalField(_(""), max_digits=5, decimal_places=2, blank=True, null=True)
    vl_boletos = models.DecimalField(_(""), max_digits=5, decimal_places=2, blank=True, null=True)
    vl_pago = models.DecimalField(_(""), max_digits=5, decimal_places=2, blank=True, null=True)
    deposito = models.DecimalField(_(""), max_digits=5, decimal_places=2, blank=True, null=True)
    repasse = models.DecimalField(_(""), max_digits=5, decimal_places=2, blank=True, null=True)

    

    class Meta:
        verbose_name = _("cad_cliente_model")
        verbose_name_plural = _("cad_cliente_models")

    def __str__(self):
        return self.nome

    def get_absolute_url(self):
        return reverse("cad_cliente_model_detail", kwargs={"pk": self.pk})



class CAD_Cliente(models.Model):
    vendedor = models.CharField(_(""), max_length=128)
    codigo = models.IntegerField(_(""))
    taxas = models.DecimalField(_("Taxas"), max_digits=5, decimal_places=2)
    sim = models.IntegerField(_(""), default=3/100)
    nao = models.IntegerField(_(""), default=20/100)
    operacional = models.IntegerField(_(""), default=5/100)
    tcc = models.DecimalField(_(""), max_digits=5, decimal_places=2, default=1/100)
    honorarios = models.DecimalField(_(""), max_digits=5, decimal_places=2, default=3/100)
    animal = models.CharField(_(""), max_length=50)
    evento = models.CharField(_(""), max_length=128)
    informar_repasse = models.CharField(_(""), max_length=50)
    vl_juros = models.DecimalField(_(""), max_digits=5, decimal_places=2)
    vl_boletos = models.DecimalField(_(""), max_digits=5, decimal_places=2)
    vl_pago = models.DecimalField(_(""), max_digits=5, decimal_places=2)
    deposito = models.DecimalField(_(""), max_digits=5, decimal_places=2)
    repasse = models.DecimalField(_(""), max_digits=5, decimal_places=2)

    

    class Meta:
        verbose_name = _("CAD_Cliente")
        verbose_name_plural = _("CAD_Clientes")

    def __str__(self):
        return self.vendedor

    def get_absolute_url(self):
        return reverse("ParametrosCliente_Repasse_detail", kwargs={"pk": self.pk})

class Repasse(models.Model):
    deposito = models.CharField(_(""), max_length=50)
    calculo = models.DecimalField(_(""), max_digits=5, decimal_places=2)
    taxas = models.DecimalField(_(""), max_digits=5, decimal_places=2)
    adi = models.BooleanField(_(""))
    me = models.DecimalField(_(""), max_digits=5, decimal_places=2)
    op = models.DecimalField(_(""), max_digits=5, decimal_places=2)
    

    class Meta:
        verbose_name = _("repasse")
        verbose_name_plural = _("repasses")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("repasse_detail", kwargs={"pk": self.pk})


class ConsolidadoVendedor(models.Model):
    contrato = models.ForeignKey(existing_models.Contratos, on_delete=models.DO_NOTHING)
    parcelas = models.ManyToManyField(existing_models.ContratoParcelas)

    class Meta:
        verbose_name = _("ConsolidadoVendedor")
        verbose_name_plural = _("ConsolidadoVendedors")

    def get_absolute_url(self):
        return reverse("ConsolidadoVendedor_detail", kwargs={"pk": self.pk})