# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse

from django.db import connection
from .models import ContratoParcela


def populate(request):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT contratos_id, dt_vencimento, vl_parcela, dt_credito from contrato_parcelas limit 10")
        result = cursor.fetchall()
        #result = ContratoParcelas.objects.filter(dt_vencimento__gte='2023-01-01')
        for row in result:
            contratos_id = row[0]
            dt_vencimento = row[1]
            vl_parcela = row[2]
            dt_credito = row[3]

            contrato_parcela = ContratoParcela(
                contratos_id=contratos_id, 
                dt_vencimento=dt_vencimento, 
                vl_parcela=vl_parcela, 
                dt_credito=dt_credito
                )
            contrato_parcela.save()

    return HttpResponseRedirect(reverse('home'))


@login_required(login_url="/login/")
def index(request):
    # *apenas para testes, é altamente recomendavel mapear as tabelas em modelos no Django
    context = {'segment': 'index'}

    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def pages(request):
    result = ()
    with connection.cursor() as cursor:
        cursor.execute('SELECT contratos_id, dt_vencimento, vl_parcela, dt_credito from contrato_parcelas where dt_vencimento>="2023-01-01" limit 10')
        result = cursor.fetchall()
    context = {'result':result}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:

        load_template = request.path.split('/')[-1]
        # print(f'{load_template = }\n {request.path = } \n {request.path.split("/")[-1] = }')

        #!Somnete o admin pode fazer registro de novos usuarios

        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        context['segment'] = load_template

        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))
