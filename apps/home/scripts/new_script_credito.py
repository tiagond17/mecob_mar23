from django.db.models import Sum
from django.shortcuts import render
from datetime import datetime, timedelta
from .models import Credito, Pessoas

def minha_view(request):
    context = {}
    pessoas = Pessoas.objects.all()
    creditos = Credito.objects.filter(dt_creditado__month=datetime.now().month)
    dias_do_mes = [(datetime.now().replace(day=1) + timedelta(days=i)).day for i in range(31)]
    
    for pessoa in pessoas:
        creditos_pessoa = creditos.filter(cliente=pessoa)
        credito_dict = {'nome': pessoa.nome, 'id': pessoa.id}
        for dia in dias_do_mes:
            valor_credito = creditos_pessoa.filter(dt_creditado__day=dia).aggregate(Sum('vl_credito'))['vl_credito__sum'] or 0
            credito_dict[f'dia_{dia}'] = valor_credito
        credito_dict['total_credito'] = creditos_pessoa.aggregate(Sum('vl_credito'))['vl_credito__sum'] or 0
        context[pessoa.id] = credito_dict
    context['dias_do_mes'] = dias_do_mes
    return render(request, 'template.html', {'context': context})
  
""" html:
{% for id, credito_dict in context.items %}
  <h2>{{ credito_dict.nome }} - ID: {{ id }}</h2>
  <table>
    <thead>
      <tr>
        <th>Data</th>
        <th>Valor</th>
      </tr>
    </thead>
    <tbody>
      {% for dia in dias_do_mes %}
        <tr>
          <td>{{ dia }}/{{ agora|date:"F" }}</td>
          <td>{{ credito_dict.f'dia_{dia}'|floatformat:2 }}</td>
        </tr>
      {% endfor %}
    </tbody>
    <tfoot>
      <tr>
        <td>Total</td>
        <td>{{ credito_dict.total_credito|floatformat:2 }}</td>
      </tr>
    </tfoot>
  </table>
{% endfor %}
"""