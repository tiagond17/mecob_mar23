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
from django.db.models import Sum
from django.db.models.functions import TruncDay, Coalesce

from django.db.models import F,Count,FloatField, Q


from .existing_models import Contratos, ContratoParcelas
from .forms import CAD_ClienteForm, Calculo_RepasseForm
from .models import CAD_Cliente_Model, Calculo_Repasse


@login_required(login_url="/login/")
def index(request):
    context = {'segment': 'index'}

    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))

def preencher_tabela(data_inicio, data_fim):
    with connection.cursor() as cursor:
        cursor.execute(f"""
SELECT
    cp.contratos_id as id_contrato,
    CASE WHEN NOT ISNULL(pev.nome) THEN pev.nome ELSE 'boleto avulso' END as vendedor,
    CASE WHEN NOT ISNULL(pec.nome) THEN pec.nome ELSE peb.nome END as comprador,
    cp.nu_parcela as nu_parcela,
    cp.vl_parcela as vl_parcela,
    cp.vl_pagto,
    cp.dt_vencimento as dt_vencimento,
    cp.dt_credito as dt_credito,
    cp.dt_processo_pagto as dt_processamento,
    CASE WHEN cp.contratos_id > 12460 OR ISNULL(cp.contratos_id) THEN 'UNICRED' ELSE 'BRADESCO' END as banco,
    co.parcela_primeiro_pagto as parcela_primeiro_pagto,
    co.nu_parcelas as tt_parcelas,
    (SELECT COUNT(*) FROM contrato_parcelas cpx 
    WHERE cpx.contratos_id = cp.contratos_id 
        AND (NOT ISNULL(dt_pagto) AND NOT dt_pagto = '0000-00-00') ) as tt_quitadas,
    ev.nome as evento,
    co.descricao as produto,
    cr.deposito,
	cr.calculo,
    cr.taxas,
    cr.adi,
    cr.me,
    cr.op,
    cr.repasses,
    cr.comissao
FROM contrato_parcelas cp
LEFT JOIN contratos co ON co.id = cp.contratos_id
LEFT JOIN boletos_avulso bo ON bo.id = cp.boletos_avulso_id
LEFT JOIN pessoas pec ON pec.id = co.comprador_id
LEFT JOIN pessoas pev ON pev.id = co.vendedor_id
LEFT JOIN pessoas peb ON peb.id = bo.pessoas_id
LEFT JOIN eventos ev ON ev.id = co.eventos_id
LEFT JOIN calculo_repasse cr ON cr.id_contrato_id = cp.contratos_id AND cr.nu_parcela = cp.nu_parcela
WHERE cp.dt_credito BETWEEN '{data_inicio}' AND '{data_fim}'
AND NOT ISNULL(arquivos_id_retorno)
ORDER BY cp.dt_credito ASC, cp.nu_parcela ASC limit 1000""")
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
            with connection.cursor() as cursor:
                cursor.execute("""
SELECT SUM(vl_pago) as total_repasses, comissao, COUNT(*) as qtde
FROM calculo_repasse
WHERE comissao IS NOT NULL AND comissao != " -" AND comissao != "-" AND comissao != "            -" AND comissao != " - "
#AND dt_credito BETWEEN '2022-08-12' AND '2022-01-23'
group by comissao""")
                result = cursor.fetchall()
                context['sql'] = result

        # se o template a ser carregado for tbl_bootstrap.html carregue contratos
        if load_template == 'tbl_bootstrap.html':
            if request.method == 'POST':
                pass
                """ # pegue as datas do form
                data_inicio = request.POST.get('data-inicio')  # 2022-08-01:str
                data_fim = request.POST.get('data-fim')  # 2022-08-21:str
                print(data_inicio, data_fim)
                
                with connection.cursor() as cursor:
                    cursor.execute("select vendedor_id, contratos.id, comprador_id, tp_contrato, status ,vl_boleto, vl_pago, vl_parcela, nu_parcelas, dados_arquivo_retorno.dt_credito, contrato_parcelas.dt_credito from dados_arquivo_retorno, contratos, contrato_parcelas where contrato_parcelas.dt_credito >= '{}' and contrato_parcelas.dt_credito <= '{}' limit 1000".format(data_inicio, data_fim))
                    result = cursor.fetchall()
                    context['sql'] = result """
            with connection.cursor() as cursor:
                cursor.execute("""
SELECT
    c.vendedor_id,
    p.nome AS nome_vendedor,
    SUM(CASE WHEN DAY(cr.dt_credito) = 1 THEN cr.repasses ELSE 0 END) AS dia_1,
    SUM(CASE WHEN DAY(cr.dt_credito) = 2 THEN cr.repasses ELSE 0 END) AS dia_2,
    SUM(CASE WHEN DAY(cr.dt_credito) = 3 THEN cr.repasses ELSE 0 END) AS dia_3,
    SUM(CASE WHEN DAY(cr.dt_credito) = 4 THEN cr.repasses ELSE 0 END) AS dia_4,
    SUM(CASE WHEN DAY(cr.dt_credito) = 5 THEN cr.repasses ELSE 0 END) AS dia_5,
    SUM(CASE WHEN DAY(cr.dt_credito) = 6 THEN cr.repasses ELSE 0 END) AS dia_6,
    SUM(CASE WHEN DAY(cr.dt_credito) = 7 THEN cr.repasses ELSE 0 END) AS dia_7,
    SUM(CASE WHEN DAY(cr.dt_credito) = 8 THEN cr.repasses ELSE 0 END) AS dia_8,
    SUM(CASE WHEN DAY(cr.dt_credito) = 9 THEN cr.repasses ELSE 0 END) AS dia_9,
    SUM(CASE WHEN DAY(cr.dt_credito) = 10 THEN cr.repasses ELSE 0 END) AS dia_10,
    SUM(CASE WHEN DAY(cr.dt_credito) = 11 THEN cr.repasses ELSE 0 END) AS dia_11,
    SUM(CASE WHEN DAY(cr.dt_credito) = 12 THEN cr.repasses ELSE 0 END) AS dia_12,
    SUM(CASE WHEN DAY(cr.dt_credito) = 13 THEN cr.repasses ELSE 0 END) AS dia_13,
    SUM(CASE WHEN DAY(cr.dt_credito) = 14 THEN cr.repasses ELSE 0 END) AS dia_14,
    SUM(CASE WHEN DAY(cr.dt_credito) = 15 THEN cr.repasses ELSE 0 END) AS dia_15,
    SUM(cr.repasses) AS total_repasses
FROM
    calculo_repasse AS cr
    INNER JOIN contratos AS c ON cr.id_contrato_id = c.id
    INNER JOIN pessoas AS p ON c.vendedor_id = p.id
WHERE
    cr.dt_credito BETWEEN '2022-09-01' AND '2022-09-15'
GROUP BY
    c.vendedor_id,
    p.nome 
                """)
                context['sql'] = cursor.fetchall()
            #context['quinzena_result'] = Calculo_Repasse.objects.select_related('id_vendedor').filter()
            
        if load_template == 'cad_clientes_table_bootstrap.html':
            context['cad_clientes'] = CAD_Cliente_Model.objects.all()
            

        if load_template == 'form_elements.html':
            if request.method == "POST":
                data_inicio = request.POST.get('data_inicio')  # 2022-08-01:str
                data_fim = request.POST.get('data_fim')  # 2022-08-21:str
                context['sql'] = preencher_tabela(data_inicio=data_inicio,data_fim=data_fim)
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
