from django.template import Library

register = Library()

@register.filter(name='sum_objects_value')
def sum_objects_value(contratos):
    return sum(
        [contrato.vl_parcela for contrato in contratos]
    )

    
@register.filter(name='test')
def test(value):
    return 'adawdwad'