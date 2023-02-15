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
from .forms import CAD_ClienteForm, Calculo_RepasseForm
from .models import CAD_Cliente_Model, Calculo_Repasse


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
        
        if load_template == 'tbl_comissoes_bootstrap.html':
            context['calculos_repasses'] = Calculo_Repasse.objects.all()[:100]

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
            
        if load_template == 'cad_clientes_table_bootstrap.html':
            context['cad_clientes'] = CAD_Cliente_Model.objects.all()[:1000]
            

        if load_template == 'form_elements.html':
            with connection.cursor() as cursor:
                cursor.execute("""
SELECT cp.contratos_id AS id_contrato,
       CASE
           WHEN NOT isnull(pev.nome) THEN pev.nome
           ELSE 'boleto avulso'
       END AS vendedor,
       CASE
           WHEN NOT isnull(pec.nome) THEN pec.nome
           ELSE peb.nome
       END AS comprador,
       cp.nu_parcela AS nu_parcela,
       cp.vl_parcela AS vl_parcela,
       cp.vl_pagto,
       cp.dt_vencimento AS dt_vencimento,
       cp.dt_credito AS dt_credito,
       cp.dt_processo_pagto AS dt_processamento,
       CASE
           WHEN cp.contratos_id > 12460
                OR isnull(cp.contratos_id) THEN 'UNICRED'
           ELSE 'BRADESCO'
       END AS banco,
       co.nu_parcelas AS tt_parcelas,

  (SELECT count(*)
   FROM contrato_parcelas cpx
   WHERE cpx.contratos_id = cp.contratos_id
     AND (NOT isnull(dt_pagto)
          AND NOT dt_pagto = '0000-00-00') ) AS tt_quitadas,
       co.parcela_primeiro_pagto AS parcela_primeiro_pagto,
       ev.nome AS evento,
       co.descricao AS produto
FROM contrato_parcelas cp
LEFT JOIN contratos co ON co.id = cp.contratos_id
LEFT JOIN boletos_avulso bo ON bo.id = cp.boletos_avulso_id
LEFT JOIN pessoas pec ON pec.id = co.comprador_id
LEFT JOIN pessoas pev ON pev.id = co.vendedor_id
LEFT JOIN pessoas peb ON peb.id = bo.pessoas_id
LEFT JOIN eventos ev ON ev.id = co.eventos_id
WHERE date(dt_credito) = '2022-09-30'
  AND NOT isnull(arquivos_id_retorno)
ORDER BY banco DESC,
         cp.contratos_id ASC""")
                #dt_processo_pagto
                #dt_credito
                #TODO: tornar essa consulta mais pratica por meio de uma função
                result = cursor.fetchall()
                context['sql'] = result
            if request.method == "POST":
                form = Calculo_RepasseForm(request.POST)
                if form.is_valid():
                    form.save()
                    print("tudo certo")
                else:
                    print(form.errors)
            context['form'] = Calculo_RepasseForm()
            #!context['cad_clientes'] = CAD_Cliente_Model.objects.all()
            

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
