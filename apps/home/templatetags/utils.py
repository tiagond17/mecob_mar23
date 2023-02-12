from django.template import Library
from apps.home.existing_models import Contratos, ContratoParcelas, Pessoas

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

#faça um metodo async para pegar o nome da pessoa
async def pegar_pessoa_pelo_id(pessoa_id):
    pessoa = await Pessoas.objects.get(id=pessoa_id)
    return pessoa.nome

@register.filter(name='pegar_pessoa_pelo_id')
def pegar_pessoa_pelo_id(pessoa_id):
    return Pessoas.objects.get(id=pessoa_id).nome

@register.filter(name='pegar_pessoa_pelo_nome')
def pegar_pessoa_pelo_nome(nome):
    pessoas = Pessoas.objects.filter(nome=nome, eh_vendedor="S")
    return [pessoa.id for pessoa in pessoas]
    """ try:
        pessoa =  Pessoas.objects.get(nome=nome, eh_vendedor="S")
        return pessoa.id
    except Pessoas.DoesNotExist:
        return 'id não encontrado'
    except Pessoas.MultipleObjectsReturned:
        pessoas = Pessoas.objects.filter(nome=nome, eh_vendedor="S")
        return [pessoa.id for pessoa in pessoas] """