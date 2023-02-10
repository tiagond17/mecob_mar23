from django.template import Library
from apps.home.existing_models import Contratos, ContratoParcelas

register = Library()

@register.filter(name='sum_valor_parcelas')
def sum_valor_parcelas(parcelas):
    return sum(
        [parcela.vl_parcela for parcela in parcelas]
    )
    
@register.filter(name='sum_total_valor_parcelas')
def sum_total_valor_parcelas(contratos, vendedor_id):
    #! Por algum motivo, apesar do contratos se do tipo QuerySet não é possivel
    #!fazer filtro (filter). Provavelmente por causa do template
    total = 0
    for contrato in contratos:
        if contrato.vendedor.id == vendedor_id:
            total += sum(
                [parcela.vl_parcela for parcela in contrato.parcelas.all()]
            )
    return total


@register.filter(name='datas_validas')
def datas_validas(parcelas):
    datas = list()
    for parcela in parcelas:
        if parcela.dt_credito:
            datas.append(parcela)
    return datas
    