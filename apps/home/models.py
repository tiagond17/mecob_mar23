# -*- encoding: utf-8 -*-

from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
import decimal
import math
"""
Copyright (c) 2019 - present AppSeed.us
"""
#*pegar o id e nome do vendedor e colocar no cad cliente

"""A tabela CadCliente é utilizada para cadastrar novos clientes no sistema
ou seja, sempre que uma pessoa (que esteja no banco de dados cadastrado na tabela Pessoa)
realizar uma venda ela é adicionada na tabela CadCliente"""
class CadCliente(models.Model):
    vendedor = models.ForeignKey('Pessoas', on_delete=models.CASCADE, blank=True, null=True)
    nome = models.CharField(_(""), max_length=128, blank=True, null=True)
    codigo = models.IntegerField(_(""), blank=True, null=True)

    taxas = models.DecimalField(_("Taxas"), max_digits=5, decimal_places=2, blank=True, null=True)
    sim = models.DecimalField(_(""), max_digits=5, decimal_places=2, blank=True, null=True)
    nao = models.DecimalField(_(""), max_digits=5, decimal_places=2, blank=True, null=True)
    operacional = models.DecimalField(_(""), max_digits=5, decimal_places=2, blank=True, null=True)
    tcc = models.DecimalField(_(""), max_digits=5, decimal_places=2, blank=True, null=True)
    honorarios = models.DecimalField(_(""), max_digits=5, decimal_places=2, blank=True, null=True)
    animal = models.CharField(_(""), max_length=256, blank=True, null=True)
    evento = models.CharField(_(""), max_length=256, blank=True, null=True)
    informar_repasse = models.CharField(_(""), max_length=50, blank=True, null=True)
    vl_juros = models.DecimalField(_(""), max_digits=5, decimal_places=2, blank=True, null=True)
    vl_boletos = models.DecimalField(_(""), max_digits=5, decimal_places=2, blank=True, null=True)
    vl_pago = models.DecimalField(_(""), max_digits=5, decimal_places=2, blank=True, null=True)
    deposito = models.DecimalField(_(""), max_digits=5, decimal_places=2, blank=True, null=True)
    repasse = models.DecimalField(_(""), max_digits=5, decimal_places=2, blank=True, null=True)


    class Meta:
        verbose_name = _("cad_cliente")
        verbose_name_plural = _("cad_clientes")
        db_table = 'cad_cliente'
        managed = True

    def __str__(self):
        return self.nome

    def get_absolute_url(self):
        return reverse("cad_cliente_model_detail", kwargs={"pk": self.pk})

class Comissao_Vendedor(models.Model):
    #id, default django
    comissao = models.DecimalField(_(""), max_digits=5, decimal_places=2)
    vendedor = models.ForeignKey('Pessoas', on_delete=models.CASCADE, blank=True, null=True)
    taxa_percentual = models.DecimalField(_(""), max_digits=5, decimal_places=2, blank=True, null=True)
    taxa_de_comissao = models.DecimalField(_(""), max_digits=5, decimal_places=2, default=1/100, blank=True, null=True)
    nome = models.CharField(_(""), max_length=128, blank=True, null=True)
    id_contrato = models.ForeignKey('Contratos', on_delete=models.CASCADE, blank=True, null=True)
    numero_contrato = models.IntegerField(_(""), blank=True, null=True)
    codigo_parcela = models.IntegerField(_(""), blank=True, null=True)

    class Meta:
        verbose_name = _("Comissao_Vendedor")
        verbose_name_plural = _("Comissao_Vendedores")
        db_table = 'comissao_vendedor'
        managed = True

    def __str__(self):
        return f'{self.nome}, comissao: {self.comissao}'

    def get_absolute_url(self):
        return reverse("Comissao_Vendedores_detail", kwargs={"pk": self.pk})

""" 
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
        return reverse("ParametrosCliente_Repasse_detail", kwargs={"pk": self.pk}) """

#?Como eu devo fazer o calculo ? do contrato geral ou da parcela ?
#?Soma tudo e depois coloca o calculo de 1% do faturamento ?

class Calculo_Repasse(models.Model):
    #id: default django
    #TODO: o id_contrato e o id_vendedor são instancias de Contratos e Pessoas, alterar o nome para vendedor e contrato
    id_vendedor = models.ForeignKey('Pessoas', on_delete=models.DO_NOTHING, blank=True, null=True)
    id_contrato = models.ForeignKey('Contratos', on_delete=models.DO_NOTHING, blank=True, null=True)
    contrato_parcelas = models.ForeignKey('ContratoParcelas', on_delete=models.DO_NOTHING, blank=True, null=True)
    deposito = models.CharField(_(""), max_length=128, blank=True, null=True)
    taxas = models.DecimalField(_(""), max_digits=12, decimal_places=2, blank=True, null=True)
    adi = models.CharField(_(""), max_length=12, blank=True, null=True)
    me = models.DecimalField(_(""), max_digits=12, decimal_places=2, blank=True, null=True)
    op = models.DecimalField(_(""), max_digits=12, decimal_places=2, blank=True, null=True)
    repasses = models.DecimalField(_(""), max_digits=12, decimal_places=2, blank=True, null=True)
    calculo = models.DecimalField(_(""), max_digits=12, decimal_places=2, blank=True, null=True)
    nu_parcela = models.IntegerField(_(""), blank=True, null=True)
    comissao = models.CharField(_(""), max_length=128, blank=True, null=True)
    dt_credito = models.DateField(_(""),blank=True, null=True)
    
    #* o vl_pago pode ser encontrado no modelo DadosArquivoRetorno
    vl_pago = models.DecimalField(_(""), max_digits=12, decimal_places=2, blank=True, null=True)
    
    repasse_calc = models.DecimalField(_(""), max_digits=12, decimal_places=2, blank=True, null=True)
    
    
    #TODO: colocar os testes feitos de feira-online aqui
    @property
    def calculo_model(self):
        return (self.vl_pago or 0) - (self.taxas or 0)
    
    @property
    def me_model(self):
        #arredondar para cima sempre
        if (self.adi in ['Sim', 'sim', 'SIM','S', 's']):
            #return self.calculo_model * 0.2
            return math.ceil(float(self.calculo_model) * 0.2)
        return math.ceil(float(self.calculo_model) * 0.03)
        #return self.calculo_model * 0.03
    
    @property
    def repasses_model(self):
        return (self.vl_pago or 0) - (self.taxas or 0) - self.me_model
    
    @property
    def get_repasses(self):
        return f'model: {self.repasses_model}'

    class Meta:
        verbose_name = _("calculo_repasse")
        verbose_name_plural = _("calculo_repasses")
        #*o nome Calculo_Repasse deveria estar como: 'calculo_repasse'
        db_table = 'Calculo_Repasse'

    def __str__(self):
        return self.get_repasses
    
    """ def save(self) -> object:
        return super().save(force_insert, force_update, using, update_fields) """

    def get_absolute_url(self):
        return reverse("calculo_repasse_detail", kwargs={"pk": self.pk})
    
""" esse modelo serve para puxar todos os dados que estão na planilha
e facilitar a consulta caso haja erro de dados no Calculo_Repasse"""
class Dado(models.Model):
    id_vendedor = models.IntegerField(_(""), blank=True, null=True)
    id_contrato = models.IntegerField(_(""), blank=True, null=True)
    vendedor = models.CharField(_(""), max_length=100, blank=True, null=True)
    comprador = models.CharField(_(""), max_length=100, blank=True, null=True)
    nu_parcela = models.CharField(_(""), max_length=100, blank=True, null=True)
    contrato = models.IntegerField(_(""), blank=True, null=True)
    vl_pago = models.DecimalField(_(""), max_digits=12, decimal_places=2, blank=True, null=True)
    dt_vencimento = models.DateField(_(""),blank=True, null=True)
    dt_credito = models.DateField(_(""),blank=True, null=True)
    banco = models.CharField(_(""), max_length=50, blank=True, null=True)
    evento = models.CharField(_(""), max_length=512, blank=True, null=True)
    deposito = models.CharField(_(""), max_length=50, blank=True, null=True)
    calculo = models.DecimalField(_(""), max_digits=12, decimal_places=2, blank=True, null=True)
    taxas = models.DecimalField(_(""), max_digits=12, decimal_places=2, blank=True, null=True)
    adi = models.CharField(_(""), max_length=12, blank=True, null=True)
    me = models.DecimalField(_(""), max_digits=12, decimal_places=2, blank=True, null=True)
    op = models.DecimalField(_(""), max_digits=12, decimal_places=2, blank=True, null=True)
    repasses = models.DecimalField(_(""), max_digits=12, decimal_places=2, blank=True, null=True)
    comissao = models.CharField(_(""), max_length=128, blank=True, null=True)

    class Meta:
        verbose_name = _("Dado")
        verbose_name_plural = _("Dados")

    def __str__(self):
        return f'{self.id_contrato}, {self.vendedor}'

    def get_absolute_url(self):
        return reverse("Dado_detail", kwargs={"pk": self.pk})


class Quinzenal(models.Model):
    def __str__(self):
        pass

    class Meta:
        db_table = 'quinzenal'
        managed = True
        verbose_name = 'Quinzenal'
        verbose_name_plural = 'Quinzenais'