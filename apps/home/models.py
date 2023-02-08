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

from . import existing_models

class ConsolidadoVendedor(models.Model):
    contrato = models.ForeignKey(existing_models.Contratos(""), on_delete=models.CASCADE)
    parcelas = models.ManyToManyField(existing_models.ContratoParcelas)

    class Meta:
        verbose_name = _("ConsolidadoVendedor")
        verbose_name_plural = _("ConsolidadoVendedors")

    def get_absolute_url(self):
        return reverse("ConsolidadoVendedor_detail", kwargs={"pk": self.pk})