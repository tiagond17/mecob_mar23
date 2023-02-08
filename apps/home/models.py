# -*- encoding: utf-8 -*-

from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
"""
Copyright (c) 2019 - present AppSeed.us
"""

from . import existing_models

class ContratoParcela(models.Model):
    contratos_id = models.IntegerField()
    dt_vencimento = models.DateField()
    vl_parcela = models.DecimalField()
    dt_credito = models.DateField()
    nu_parcela = models.PositiveIntegerField()


    class Meta:
        verbose_name = _("ContratoParcela")
        verbose_name_plural = _("ContratoParcelas")
        managed=False
        db_table='contrato_parcelas'

    def __str__(self):
        return f'Model ID:{self.pk}, ContratoID: {self.contratos_id}'

    def get_absolute_url(self):
        return reverse("ContratoParcela_detail", kwargs={"pk": self.pk})
