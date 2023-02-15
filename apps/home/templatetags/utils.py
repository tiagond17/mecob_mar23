from django.template import Library
from apps.home.existing_models import Contratos, ContratoParcelas, Pessoas
from apps.home.models import Calculo_Repasse

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
        
@register.filter(name='pegar_repasse_pelo_id_contrato')
def pegar_repasse_pelo_id_contrato(id_contrato):
    try:
        calculos = Calculo_Repasse.objects.filter(id_contrato=id_contrato)
        return calculos
        """ if calculos.count() > 1:
            return calculos[0]
        else:
            return [calculo.repasses for calculo in calculos] """
    except Calculo_Repasse.DoesNotExist:
        return 'id não encontrado'
    
@register.filter('calcular_comissao')
def calcular_comissao(vendedor, repasse):
    #repasse is a str
    if vendedor.nome:
        #coloque apenas 2 casas decimais apos a virgula
        return float(repasse) * 0.05
        
    return float(repasse) * 0.1
    """ if vendedor.nome:
        return repasse * 0.05
    return repasse * 0.1 """

        