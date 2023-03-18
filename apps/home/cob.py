from django.db import models

class Pessoa(models.Model):
    nome = models.CharField(max_length=100)

class Produto(models.Model):
    nome = models.CharField(max_length=100)
    tipo_venda = models.CharField(max_length=50)

class Contrato(models.Model):
    vendedor = models.ForeignKey(Pessoa, on_delete=models.CASCADE, related_name='vendedor_contratos')
    compradores = models.ManyToManyField(Pessoa, related_name='comprador_contratos')
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    # Outros campos do contrato

class Parcela(models.Model):
    contrato = models.ForeignKey(Contrato, on_delete=models.CASCADE, related_name='parcelas')
    valor = models.DecimalField(max_digits=12, decimal_places=2)
    data_credito = models.DateField()
    data_vencimento = models.DateField()
    numero_parcela = models.PositiveIntegerField()
    # Outros campos da parcela

class Rateio(models.Model):
    contrato = models.ForeignKey(Contrato, on_delete=models.CASCADE, related_name='rateios')
    comprador = models.ForeignKey(Pessoa, on_delete=models.CASCADE)
    valor_rateio = models.DecimalField(max_digits=12, decimal_places=2)
    # Outros campos do rateio
