# -*- encoding: utf-8 -*-

""" MODELOS QUE IREMOS USAR
contrato_parcela"""
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
"""
Copyright (c) 2019 - present AppSeed.us
"""


class ContratoParcela(models.Model):
    contratos_id = models.IntegerField()
    dt_vencimento = models.DateField()
    vl_parcela = models.DecimalField(max_digits=10, decimal_places=2)
    dt_credito = models.DateField()

    class Meta:
        verbose_name = _("ContratoParcela")
        verbose_name_plural = _("ContratoParcelas")
        managed=False
        db_table='contrato_parcelas'

    def __str__(self):
        return f'Model DJ:{self.pk}, ContratoID: {self.contratos_id}'

    def get_absolute_url(self):
        return reverse("ContratoParcela_detail", kwargs={"pk": self.pk})
