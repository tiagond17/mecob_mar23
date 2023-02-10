# -*- encoding: utf-8 -*-

from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
"""
Copyright (c) 2019 - present AppSeed.us
"""
#*consolidado_vendedor, nome sugerido por Tiago para nova tabela utilizando os dados de contratos e contrato_parcelas
#TODO:  selecionar o que vendedo e totalizar quanto ele tem para recebe entre agosto/22
#! Colocar uma feature em que é possivel filtrar por data de vencimento
#Todo: Todas as parcelas de uma determinada data, e some o valor de cada e organize por vendedor
#TODO:
from . import existing_models


class CAD_Cliente(models.Model):
    taxas = models.DecimalField(_("Taxas"), max_digits=5, decimal_places=2)
    id_vendedor = models.CharField(_(""), max_length=50)
    vendedor = models.CharField(_(""), max_length=128)
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
    #eventos
    
    """ @property
    def calculo(self):
        return self. """
    

    class Meta:
        verbose_name = _("ParametrosCliente_Repasse")
        verbose_name_plural = _("ParametrosCliente_Repasses")

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