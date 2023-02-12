# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
from datetime import datetime
from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.shortcuts import render
from django.db import connection, connections

from .existing_models import Contratos, ContratoParcelas
from .forms import CAD_ClienteForm
from .models import CAD_Cliente, CAD_Cliente_Model


@login_required(login_url="/login/")
def index(request):
    context = {'segment': 'index'}

    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))

def preencher_tabela(data_inicio, data_fim):
    if not data_inicio and not data_fim:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM contrato_parcelas, contratos, dados_arquivo_retorno limit 10")
            result = cursor.fetchall()
            return result
        

@login_required(login_url="/login/")
def pages(request):
    context = {}
        
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:

        load_template = request.path.split('/')[-1]
        
        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        context['segment'] = load_template

        # se o template a ser carregado for tbl_bootstrap.html carregue contratos
        if load_template == 'tbl_bootstrap.html':
            if request.method == 'POST':
                # pegue as datas do form
                data_inicio = request.POST.get('data-inicio')  # 2022-08-01:str
                data_fim = request.POST.get('data-fim')  # 2022-08-21:str
                print(data_inicio, data_fim)
                
                with connection.cursor() as cursor:
                    cursor.execute("select vendedor_id, contratos.id, comprador_id, tp_contrato, status ,vl_boleto, vl_pago, vl_parcela, nu_parcelas, dados_arquivo_retorno.dt_credito, contrato_parcelas.dt_credito from dados_arquivo_retorno, contratos, contrato_parcelas where contrato_parcelas.dt_credito >= '{}' and contrato_parcelas.dt_credito <= '{}' limit 1000".format(data_inicio, data_fim))
                    result = cursor.fetchall()
                    context['sql'] = result
            context['contratos'] = Contratos.objects.all()[:30]

        if load_template == 'form_elements.html':
            context['form'] = CAD_ClienteForm()
            context['cad_clientes'] = CAD_Cliente_Model.objects.all()
            

        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    """ except:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request)) """

# no mes de setembro quero ver os vendedores em aberto, os contratos
# filtro pela data de vencimento dia 1 do 8 ate 21 do 8


def consulta_por_data(request):
    context: dict = {}
    if request.method == 'POST':
        data_inicio = request.POST.get('data-inicio')  # 2022-08-01:str
        data_fim = request.POST.get('data-fim')  # 2022-08-21:str
        date_data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d').date()
        date_date_fim = datetime.strptime(data_fim, '%Y-%m-%d').date()
        # selecione todos os contratos em que as suas parcelas estejam dentro do intervalo de datas
        #contratos = Contratos.objects.filter(parcelas__dt_credito__range=(date_data_inicio, date_date_fim))[:30]
        contratos = Contratos.objects.filter(
            parcelas__dt_credito__gte=date_data_inicio, parcelas__dt_credito__lte=date_date_fim)[:100]
        parcelas = ContratoParcelas.objects.filter(
            dt_credito__gte=date_data_inicio, dt_credito__lte=date_date_fim)[:100]
        # Cannot filter a query once a slice has been taken.
        #parcelas = contratos.filter(dt_credito__gte=date_data_inicio, dt_credito__lte=date_date_fim)

        context = {'contratos': contratos, 'parcelas': parcelas}

        return render(request, 'home/tbl_bootstrap.html', context=context)

    return HttpResponse('<h1>GET</h1>')


def criar_cad_cliente(request):
    #!repasse = valor - taxa - me
    #!calc = valor - taxa
    context = {}
    """ Aplicar os calculos da planilha aqui """
    if request.method == "post":
        return HttpResponse('<h1>POST</h1>')
    with connection.cursor() as cursor:
        cursor.execute("SELECT tp_contrato, status ,vl_boleto, vl_pago, vl_parcela, nu_parcelas, dados_arquivo_retorno.dt_credito, contrato_parcelas.dt_credito FROM dados_arquivo_retorno, contratos, contrato_parcelas LIMIT 10")
        result = cursor.fetchall()
        context['sql'] = result
    return HttpResponse('<h1>GET, {}</h1>'.format(context['sql']))
