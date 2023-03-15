# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
from django.utils.text import slugify
from datetime import datetime, date, timedelta
from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.shortcuts import render
from django.db import connection
from django.conf import settings
import random
#importe letras
import tempfile
import os
import json
import openpyxl
from decimal import Decimal
from openpyxl.utils import get_column_letter


from .existing_models import Contratos, ContratoParcelas, Pessoas, Eventos
#from .forms import CAD_ClienteForm, Calculo_RepasseForm
from .models import Calculo_Repasse, CadCliente, Debito, Credito, Taxa, RepasseRetido

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        return super().default(obj)


@login_required(login_url="/login/")
def index(request):
    context = {'segment': 'index'}

    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))


def preencher_tabela_cob(data_inicio, data_fim):
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
ORDER BY cp.dt_credito ASC, cp.nu_parcela ASC""")
        result = cursor.fetchall()
        return result


@login_required(login_url="/login/")
def pages(request):
    context = {}

    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:
        request.session['serialized_data'] = None
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

        elif load_template == 'tbl_bootstrap.html':
            if request.method == 'POST':
                pass
        
        elif load_template == 'tbl_boletos_avulso.html':
            if request.method == 'POST':
                data_inicial = request.POST.get('data-inicio')
                data_fim = request.POST.get('data-fim')
                with connection.cursor() as cursor:
                    cursor.execute(f"""
                                   SELECT
                cp.contratos_id as id_contrato,
                case when not isnull(pev.nome) then pev.nome else 'boleto avulso' end as vendedor,
                case when not isnull(pec.nome) then pec.nome else peb.nome end as comprador,
                cp.nu_parcela as nu_parcela,
                cp.vl_parcela as vl_parcela,
                cp.vl_pagto,
                cp.dt_vencimento as dt_vencimento,
                cp.dt_credito as dt_credito,
                cp.dt_processo_pagto as dt_processamento,
                case when cp.contratos_id > 12460 or isnull(cp.contratos_id) then 'UNICRED' else 'BRADESCO' end as banco,
                co.parcela_primeiro_pagto as parcela_primeiro_pagto,
                co.nu_parcelas as tt_parcelas,
                (select count(*) from contrato_parcelas cpx 
                where cpx.contratos_id = cp.contratos_id 
                    and (not isnull(dt_pagto) and not dt_pagto = '0000-00-00') ) as tt_quitadas,
                ev.nome as evento,
                co.descricao as produto
                
            FROM contrato_parcelas cp
            LEFT JOIN contratos co on co.id = cp.contratos_id
            LEFT JOIN boletos_avulso bo on bo.id = cp.boletos_avulso_id
            LEFT JOIN pessoas pec on pec.id = co.comprador_id
            LEFT JOIN pessoas pev on pev.id = co.vendedor_id
            LEFT JOIN pessoas peb on peb.id = bo.pessoas_id
            LEFT JOIN eventos ev on ev.id = co.eventos_id
            where date(dt_credito) >= '{data_inicial}' AND date(dt_credito) <= '{data_fim}' and isnull(cp.contratos_id)
            and not isnull(arquivos_id_retorno)
            order by banco desc, cp.contratos_id  asc""")
                    context['boletos_avulso'] = cursor.fetchall()
                #context['boletos_avulso'] = ContratoParcelas.objects.filter(contratos__isnull=True, dt_credito__gte=data_inicial, dt_credito__lte=data_fim)
            pass

        elif load_template == 'cad_clientes_table_bootstrap.html':
            context['cad_clientes'] = CadCliente.objects.all()
            pass
            
        elif load_template == 'tbl_julia_bootstrap.html':
            if request.method == 'POST':
                bancos = request.POST.get('bancos')
                data = request.POST.get('data')
                with connection.cursor() as cursor:
                    cursor.execute(f"""
                                select SUM(vl_pago) as valor_pago,
                                sum(me) as honorarios
                                from calculo_repasse
                                where dt_credito = '{data}' and banco='{str(bancos).upper()}';
                            """)
                    context['valores_totais'] = cursor.fetchall()
                    cursor.execute(f"""
                        select distinct comissao as comissionista,
                        sum(op) as comissoes
                        from calculo_repasse
                        where dt_credito = '{data}' and banco='{str(bancos).upper()}' and not isnull(comissao)
                        group by comissao;
                        """)
                    context['comissoes'] = cursor.fetchall()
                    cursor.execute(f"""
                        select id_contrato_id,
                        pessoas.nome,
                        CASE WHEN id_contrato_id > 12460 OR ISNULL(id_contrato_id)
                        THEN 'UNICRED' ELSE 'BRADESCO' END as banco,
                        sum(repasses)
                        from calculo_repasse
                        left join contratos on contratos.id=id_contrato_id
                        left join pessoas on pessoas.id = contratos.vendedor_id
                        where dt_credito = '{data}'
                        group by contratos.vendedor_id
                    """)
                    context['repasses'] = cursor.fetchall()
                    #context['repasses_geral'] = sum([float(calculo_repase.repasses) for calculo_repase in Calculo_Repasse.objects.filter(dt_credito=data, banco=bancos)])
                pass
            pass
        
            

            
        elif load_template == 'form_elements.html':
            if request.method == "POST":
                data_inicio = request.POST.get('data_inicio')  # 2022-08-01:str
                data_fim = request.POST.get('data_fim')  # 2022-08-21:str
                context['sql'] = preencher_tabela_cob(
                    data_inicio=data_inicio, data_fim=data_fim)
                request.session['serialized_data'] = json.dumps(context['sql'], cls=CustomJSONEncoder)
            #!context['cad_clientes'] = CadCliente.objects.all()

        elif load_template == 'tbl_credito_cessao.html':
            if request.method == "POST":
                pass
                context['nothing'] = None
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT distinct vendedor_id,
                    nome, 
                    nu_parcelas, 
                    dt_contrato FROM contratos
                    join pessoas
                    where (dt_contrato >= '2022-09-01' and dt_contrato <= '2022-09-30')
                    and repasse = 'S' and pessoas.id=vendedor_id
                    order by contratos.id desc
                    """
                )
                context['sql'] = cursor.fetchall()
                cursor.execute("""
                    SELECT
                        pc.nome AS Credor,
                        pd.nome AS Pagador,
                        c.dt_creditado as `Data`,
                        c.vl_credito AS `Valor Creditado`,
                        -d.vl_debito AS `Valor Debitado`,
                        c.descricao AS Descricao
                    FROM credito c
                    LEFT JOIN debito d ON d.dt_debitado = c.dt_creditado and d.vl_debito = c.vl_credito
                    LEFT JOIN pessoas pc ON pc.id = c.cliente_id
                    LEFT JOIN pessoas pd ON pd.id = d.cliente_id
                    WHERE c.dt_creditado >= '2022-03-02'
                    GROUP BY pc.nome, pd.nome, c.vl_credito, d.vl_debito, c.descricao;
                """)
                context['creditos_e_debitos_sql'] = cursor.fetchall()
                cursor.execute("""
                    SELECT p.id, p.nome AS nome_credor, c.dt_creditado,
                    SUM(CASE WHEN DAY(c.dt_creditado) = 1 THEN c.vl_credito ELSE 0 END) AS dia_1,
                    SUM(CASE WHEN DAY(c.dt_creditado) = 2 THEN c.vl_credito ELSE 0 END) AS dia_2,
                    SUM(CASE WHEN DAY(c.dt_creditado) = 3 THEN c.vl_credito ELSE 0 END) AS dia_3,
                    SUM(CASE WHEN DAY(c.dt_creditado) = 4 THEN c.vl_credito ELSE 0 END) AS dia_4,
                    SUM(CASE WHEN DAY(c.dt_creditado) = 5 THEN c.vl_credito ELSE 0 END) AS dia_5,
                    SUM(CASE WHEN DAY(c.dt_creditado) = 6 THEN c.vl_credito ELSE 0 END) AS dia_6,
                    SUM(CASE WHEN DAY(c.dt_creditado) = 7 THEN c.vl_credito ELSE 0 END) AS dia_7,
                    SUM(CASE WHEN DAY(c.dt_creditado) = 8 THEN c.vl_credito ELSE 0 END) AS dia_8,
                    SUM(CASE WHEN DAY(c.dt_creditado) = 9 THEN c.vl_credito ELSE 0 END) AS dia_9,
                    SUM(CASE WHEN DAY(c.dt_creditado) = 10 THEN c.vl_credito ELSE 0 END) AS dia_10,
                    SUM(CASE WHEN DAY(c.dt_creditado) = 11 THEN c.vl_credito ELSE 0 END) AS dia_11,
                    SUM(CASE WHEN DAY(c.dt_creditado) = 12 THEN c.vl_credito ELSE 0 END) AS dia_12,
                    SUM(CASE WHEN DAY(c.dt_creditado) = 13 THEN c.vl_credito ELSE 0 END) AS dia_13,
                    SUM(CASE WHEN DAY(c.dt_creditado) = 14 THEN c.vl_credito ELSE 0 END) AS dia_14,
                    SUM(CASE WHEN DAY(c.dt_creditado) = 15 THEN c.vl_credito ELSE 0 END) AS dia_15,
                    SUM(CASE WHEN DAY(c.dt_creditado) = 16 THEN c.vl_credito ELSE 0 END) AS dia_16,
                    SUM(CASE WHEN DAY(c.dt_creditado) = 17 THEN c.vl_credito ELSE 0 END) AS dia_17,
                    SUM(CASE WHEN DAY(c.dt_creditado) = 18 THEN c.vl_credito ELSE 0 END) AS dia_18,
                    SUM(CASE WHEN DAY(c.dt_creditado) = 19 THEN c.vl_credito ELSE 0 END) AS dia_19,
                    SUM(CASE WHEN DAY(c.dt_creditado) = 20 THEN c.vl_credito ELSE 0 END) AS dia_20,
                    SUM(CASE WHEN DAY(c.dt_creditado) = 21 THEN c.vl_credito ELSE 0 END) AS dia_21,
                    SUM(CASE WHEN DAY(c.dt_creditado) = 22 THEN c.vl_credito ELSE 0 END) AS dia_22,
                    SUM(CASE WHEN DAY(c.dt_creditado) = 23 THEN c.vl_credito ELSE 0 END) AS dia_23,
                    SUM(CASE WHEN DAY(c.dt_creditado) = 24 THEN c.vl_credito ELSE 0 END) AS dia_24,
                    SUM(CASE WHEN DAY(c.dt_creditado) = 25 THEN c.vl_credito ELSE 0 END) AS dia_25,
                    SUM(CASE WHEN DAY(c.dt_creditado) = 26 THEN c.vl_credito ELSE 0 END) AS dia_26,
                    SUM(CASE WHEN DAY(c.dt_creditado) = 27 THEN c.vl_credito ELSE 0 END) AS dia_27,
                    SUM(CASE WHEN DAY(c.dt_creditado) = 28 THEN c.vl_credito ELSE 0 END) AS dia_28,
                    SUM(CASE WHEN DAY(c.dt_creditado) = 29 THEN c.vl_credito ELSE 0 END) AS dia_29,
                    SUM(CASE WHEN DAY(c.dt_creditado) = 30 THEN c.vl_credito ELSE 0 END) AS dia_30,
                    SUM(CASE WHEN DAY(c.dt_creditado) = 31 THEN c.vl_credito ELSE 0 END) AS dia_31,
                    SUM(c.vl_credito) AS total_credito
                    FROM credito AS c
                    JOIN pessoas AS p ON c.cliente_id = p.id
                    WHERE c.dt_creditado >= '2022-03-01'
                    GROUP BY p.id, p.nome
                """)
                context['creditos'] = cursor.fetchall()
                cursor.execute("""
                               SELECT p.id, p.nome AS `Nome do Pagador`, c.dt_debitado,
                    SUM(CASE WHEN DAY(c.dt_debitado) = 1 THEN c.vl_debito ELSE 0 END) AS dia_1,
                    SUM(CASE WHEN DAY(c.dt_debitado) = 2 THEN c.vl_debito ELSE 0 END) AS dia_2,
                    SUM(CASE WHEN DAY(c.dt_debitado) = 3 THEN c.vl_debito ELSE 0 END) AS dia_3,
                    SUM(CASE WHEN DAY(c.dt_debitado) = 4 THEN c.vl_debito ELSE 0 END) AS dia_4,
                    SUM(CASE WHEN DAY(c.dt_debitado) = 5 THEN c.vl_debito ELSE 0 END) AS dia_5,
                    SUM(CASE WHEN DAY(c.dt_debitado) = 6 THEN c.vl_debito ELSE 0 END) AS dia_6,
                    SUM(CASE WHEN DAY(c.dt_debitado) = 7 THEN c.vl_debito ELSE 0 END) AS dia_7,
                    SUM(CASE WHEN DAY(c.dt_debitado) = 8 THEN c.vl_debito ELSE 0 END) AS dia_8,
                    SUM(CASE WHEN DAY(c.dt_debitado) = 9 THEN c.vl_debito ELSE 0 END) AS dia_9,
                    SUM(CASE WHEN DAY(c.dt_debitado) = 10 THEN c.vl_debito ELSE 0 END) AS dia_10,
                    SUM(CASE WHEN DAY(c.dt_debitado) = 11 THEN c.vl_debito ELSE 0 END) AS dia_11,
                    SUM(CASE WHEN DAY(c.dt_debitado) = 12 THEN c.vl_debito ELSE 0 END) AS dia_12,
                    SUM(CASE WHEN DAY(c.dt_debitado) = 13 THEN c.vl_debito ELSE 0 END) AS dia_13,
                    SUM(CASE WHEN DAY(c.dt_debitado) = 14 THEN c.vl_debito ELSE 0 END) AS dia_14,
                    SUM(CASE WHEN DAY(c.dt_debitado) = 15 THEN c.vl_debito ELSE 0 END) AS dia_15,
                    SUM(CASE WHEN DAY(c.dt_debitado) = 16 THEN c.vl_debito ELSE 0 END) AS dia_16,
                    SUM(CASE WHEN DAY(c.dt_debitado) = 17 THEN c.vl_debito ELSE 0 END) AS dia_17,
                    SUM(CASE WHEN DAY(c.dt_debitado) = 18 THEN c.vl_debito ELSE 0 END) AS dia_18,
                    SUM(CASE WHEN DAY(c.dt_debitado) = 19 THEN c.vl_debito ELSE 0 END) AS dia_19,
                    SUM(CASE WHEN DAY(c.dt_debitado) = 20 THEN c.vl_debito ELSE 0 END) AS dia_20,
                    SUM(CASE WHEN DAY(c.dt_debitado) = 21 THEN c.vl_debito ELSE 0 END) AS dia_21,
                    SUM(CASE WHEN DAY(c.dt_debitado) = 22 THEN c.vl_debito ELSE 0 END) AS dia_22,
                    SUM(CASE WHEN DAY(c.dt_debitado) = 23 THEN c.vl_debito ELSE 0 END) AS dia_23,
                    SUM(CASE WHEN DAY(c.dt_debitado) = 24 THEN c.vl_debito ELSE 0 END) AS dia_24,
                    SUM(CASE WHEN DAY(c.dt_debitado) = 25 THEN c.vl_debito ELSE 0 END) AS dia_25,
                    SUM(CASE WHEN DAY(c.dt_debitado) = 26 THEN c.vl_debito ELSE 0 END) AS dia_26,
                    SUM(CASE WHEN DAY(c.dt_debitado) = 27 THEN c.vl_debito ELSE 0 END) AS dia_27,
                    SUM(CASE WHEN DAY(c.dt_debitado) = 28 THEN c.vl_debito ELSE 0 END) AS dia_28,
                    SUM(CASE WHEN DAY(c.dt_debitado) = 29 THEN c.vl_debito ELSE 0 END) AS dia_29,
                    SUM(CASE WHEN DAY(c.dt_debitado) = 30 THEN c.vl_debito ELSE 0 END) AS dia_30,
                    SUM(CASE WHEN DAY(c.dt_debitado) = 31 THEN c.vl_debito ELSE 0 END) AS dia_31,
                    SUM(c.vl_debito) AS total_debito
                    FROM debito AS c
                    JOIN pessoas AS p ON c.cliente_id = p.id
                    WHERE c.dt_debitado >= '2022-03-01'
                    GROUP BY p.id, p.nome
                    """)
                context['debitos'] = cursor.fetchall()
            #context['taxas'] = Taxa.objects.filter(dt_taxa__range=('2022-01-01', '2023-03-02'), taxas__gt=0)
            #context['repasse_retido'] = RepasseRetido.objects.filter(dt_rep_retido__gt="2022-03-01")

            
        elif load_template == 'tbl_mensal_bootstrap.html':
            if request.method == 'POST':
                pass
            with connection.cursor() as cursor:
                #! provavelmente seria melhor utilizar o cp.dt_credito ao inves do cr.dt_credito
                #! Transforma esse codigo sql em ORM
                cursor.execute(
                    """
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
                        SUM(CASE WHEN DAY(cr.dt_credito) = 16 THEN cr.repasses ELSE 0 END) AS dia_16,
                        SUM(CASE WHEN DAY(cr.dt_credito) = 17 THEN cr.repasses ELSE 0 END) AS dia_17,
                        SUM(CASE WHEN DAY(cr.dt_credito) = 18 THEN cr.repasses ELSE 0 END) AS dia_18,
                        SUM(CASE WHEN DAY(cr.dt_credito) = 19 THEN cr.repasses ELSE 0 END) AS dia_19,
                        SUM(CASE WHEN DAY(cr.dt_credito) = 20 THEN cr.repasses ELSE 0 END) AS dia_20,
                        SUM(CASE WHEN DAY(cr.dt_credito) = 21 THEN cr.repasses ELSE 0 END) AS dia_21,
                        SUM(CASE WHEN DAY(cr.dt_credito) = 22 THEN cr.repasses ELSE 0 END) AS dia_22,
                        SUM(CASE WHEN DAY(cr.dt_credito) = 23 THEN cr.repasses ELSE 0 END) AS dia_23,
                        SUM(CASE WHEN DAY(cr.dt_credito) = 24 THEN cr.repasses ELSE 0 END) AS dia_24,
                        SUM(CASE WHEN DAY(cr.dt_credito) = 25 THEN cr.repasses ELSE 0 END) AS dia_25,
                        SUM(CASE WHEN DAY(cr.dt_credito) = 26 THEN cr.repasses ELSE 0 END) AS dia_26,
                        SUM(CASE WHEN DAY(cr.dt_credito) = 27 THEN cr.repasses ELSE 0 END) AS dia_27,
                        SUM(CASE WHEN DAY(cr.dt_credito) = 28 THEN cr.repasses ELSE 0 END) AS dia_28,
                        SUM(CASE WHEN DAY(cr.dt_credito) = 29 THEN cr.repasses ELSE 0 END) AS dia_29,
                        SUM(CASE WHEN DAY(cr.dt_credito) = 30 THEN cr.repasses ELSE 0 END) AS dia_30,
                        SUM(CASE WHEN DAY(cr.dt_credito) = 31 THEN cr.repasses ELSE 0 END) AS dia_31,
                        SUM(cr.repasses) AS total_mes
                    FROM 
                        Calculo_Repasse AS cr 
                        INNER JOIN contratos AS c ON cr.id_contrato_id = c.id 
                        INNER JOIN pessoas AS p ON c.vendedor_id = p.id
                    WHERE 
                        MONTH(cr.dt_credito) = 9 AND YEAR(cr.dt_credito) = 2022 -- exemplo para fevereiro de 2022
                    GROUP BY 
                        c.vendedor_id, p.nome
                    """
                )
                context['sql'] = cursor.fetchall()
                #context['repasses_retidos'] = RepasseRetido.objects.filter(dt_rep_retido__gte="2022-01-01")
                
        elif load_template == 'tbl_debito_cessao.html':
            if request.method == 'POST':
                pass
                context['nothing'] = None
                
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT distinct vendedor_id, nome , nu_parcelas, dt_contrato FROM contratos
                    join pessoas
                    where (dt_contrato >= '2022-09-01' and dt_contrato <= '2022-09-30')
                    and repasse = 'S' and pessoas.id=vendedor_id
                    order by contratos.id desc;
                    """
                )
                context['sql'] = cursor.fetchall()
                
        elif load_template == 'pessoa_info.html':
            if request.method == 'POST':
                pass
            context['pessoa'] = Pessoas.objects.get(id=733 or None)
                
            

        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    """ except:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request)) """


def consulta_por_data(request):
    context: dict = {}
    if request.method == 'POST':
        data_inicio = request.POST.get('data-inicio')  # 2022-08-01:str
        data_fim = request.POST.get('data-fim')  # 2022-08-21:str
        date_data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d').date()
        date_date_fim = datetime.strptime(data_fim, '%Y-%m-%d').date()
        #selecione todos os contratos em que as suas parcelas estejam dentro do intervalo de datas
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
    context = {}
    """ Aplicar os calculos da planilha aqui """
    if request.method == "POST":
        return HttpResponse('<h1>POST</h1>')
    with connection.cursor() as cursor:
        cursor.execute("SELECT tp_contrato, status ,vl_boleto, vl_pago, vl_parcela, nu_parcelas, dados_arquivo_retorno.dt_credito, contrato_parcelas.dt_credito FROM dados_arquivo_retorno, contratos, contrato_parcelas LIMIT 10")
        result = cursor.fetchall()
        context['sql'] = result
    return HttpResponse('<h1>GET, {}</h1>'.format(context['sql']))

def criar_novo_cadastro_de_credito_e_debito(request, *args, **kwargs):
    #pegue os valores vindo do form, eles são: credor, pagador, valor, data-credito e descricao
    if request.method == 'POST':
        credor = request.POST.get('credor')
        pagador = request.POST.get('pagador')
        valor = request.POST.get('valor')
        data_credito = request.POST.get('data-credito')
        #data_credito = datetime.strptime(request.POST.get('data-credito'), '%Y-%m-%d').date()
        descricao = request.POST.get('descricao')
        pagador = Pessoas.objects.get(id=pagador)
        credor = Pessoas.objects.get(id=credor)
        """ Debito.objects.create(
            cliente = pagador,
            vl_debito = valor,
            dt_debitado = data_credito,
            descricao = descricao,
        ) """
        """ Credito.objects.create(
            cliente = credor,
            vl_credito = valor,
            dt_creditado = data_credito,
            descricao = descricao,
        ) """
        return HttpResponseRedirect('/tbl_credito_cessao.html')
    return HttpResponse("<h1>GET OR ANY REQUEST</h1>")

def criar_nova_taxa(request):
    if request.method == 'POST':
        try:
            cliente = Pessoas.objects.get(id=request.POST.get('id-cliente'))
        except Pessoas.DoesNotExist:
            return HttpResponse("<h1>Pessoa não Encontrada</h1>")
        except Pessoas.MultipleObjectsReturned:
            return HttpResponse("<h1>Erro: Mais de uma pessoa encontrada</h1>")
        taxas = request.POST.get('taxas')
        tipo = request.POST.get('tipo')
        descricao_taxa = request.POST.get('descricao-taxa')
        data_taxa = request.POST.get('data-taxa')
        """ Taxa.objects.create(
            cliente = cliente,
            tipo = tipo,
            descricao = descricao_taxa,
            taxas = taxas,
            dt_taxa = data_taxa
        ) """
        return HttpResponseRedirect('/tbl_credito_cessao.html')
    return HttpResponse("<h1>GET OR ANY REQUEST</h1>")

def criar_novo_repasse_retido(request, *args, **kwargs):
    if request.method == 'POST':
        id_cliente = request.POST.get('id-cliente')
        valor = request.POST.get('valor')
        tipo = request.POST.get('tipo')
        data_repasse_retido = request.POST.get('data-repasse-retido')
        """ RepasseRetido.objects.create(
            cliente=Pessoas.objects.get(id=id_cliente),
            vlr_rep_retido=valor,
            tipo = tipo,
            dt_rep_retido = data_repasse_retido
        ) """
        return HttpResponseRedirect('/tbl_credito_cessao.html')
    return HttpResponse(" <h1>GET</h1> ")

def filtrar_tabela_quinzenal(request, *args, **kwargs):
    context:dict = dict()
    if request.method == 'POST':
        data_inicio = request.POST.get('data-inicio')
        data_fim = request.POST.get('data-fim')
        data_inicio_dt = datetime.strptime(data_inicio, '%Y-%m-%d')
        data_fim_dt = datetime.strptime(data_fim, '%Y-%m-%d')
        
        dias_de_consulta = [(data_inicio_dt + timedelta(days=x)).day for x in range((data_fim_dt - data_inicio_dt).days + 1)]

        dias = []
        for dia in dias_de_consulta:
            dias.append(f"SUM(CASE WHEN DAY(cr.dt_credito) = {dia} THEN cr.repasses ELSE 0 END) AS dia_{dia}")
            
        consulta = f"""
        SELECT
            c.vendedor_id,
            p.nome AS nome_vendedor,
            repasse_retido.vlr_rep_retido as valor_repasse_retido,
            {', '.join(dias)},
            SUM(DISTINCT credito.vl_credito) as tt_creditos,
            SUM(DISTINCT taxas.taxas) as tt_taxas,
            SUM(DISTINCT debito.vl_debito) as tt_debitos,
            SUM(cr.repasses)
                + SUM(DISTINCT COALESCE(repasse_retido.vlr_rep_retido,0))
                - SUM(DISTINCT COALESCE(debito.vl_debito, 0))
                - SUM(DISTINCT COALESCE(taxas.taxas, 0))
                + SUM(DISTINCT COALESCE(credito.vl_credito, 0))
                AS total_repasses
        FROM
            calculo_repasse AS cr
            INNER JOIN contratos AS c ON cr.id_contrato_id = c.id
            INNER JOIN pessoas AS p ON c.vendedor_id = p.id
            LEFT JOIN (
            SELECT cliente_id, SUM(vl_credito) AS vl_credito 
            FROM credito
            WHERE dt_creditado BETWEEN '{data_inicio}' AND '{data_fim}'
            GROUP BY cliente_id
            )
            AS credito ON credito.cliente_id = c.vendedor_id
            LEFT JOIN (
            SELECT cliente_id, SUM(vl_debito) AS vl_debito 
            FROM debito
            WHERE dt_debitado BETWEEN '{data_inicio}' AND '{data_fim}'
            GROUP BY cliente_id
            )
            AS debito ON debito.cliente_id = c.vendedor_id
            LEFT JOIN (
                SELECT cliente_id, SUM(taxas) as taxas
                FROM taxas
                WHERE dt_taxa BETWEEN '{data_inicio}' AND '{data_fim}'
                GROUP BY cliente_id
            )
            as taxas on taxas.cliente_id = c.vendedor_id
            LEFT JOIN (
                SELECT cliente_id, SUM(vlr_rep_retido) as vlr_rep_retido
                from repasse_retido
                WHERE dt_rep_retido BETWEEN '{data_inicio}' AND '{data_fim}'
                group by cliente_id
            )
            as repasse_retido on repasse_retido.cliente_id = c.vendedor_id
            WHERE
            cr.dt_credito BETWEEN '{data_inicio}' AND '{data_fim}' and c.repasse = 'S'
            GROUP BY
            c.vendedor_id, p.nome
        """
    
        with connection.cursor() as cursor:
            cursor.execute(consulta)
            context['data'] = cursor.fetchall()
        
        request.session['serialized_data'] = json.dumps(context['data'], cls=CustomJSONEncoder)
        
        context['dias_de_consulta'] = dias_de_consulta
        tbody = ""
        for resultado in context['data']:
            vendedor_id = resultado[0]
            nome_vendedor = resultado[1]
            valor_repasse_retido = resultado[2]
            #dt_credito = resultado[3]
            valores_diarios = resultado[3:-4]
            total_creditos = resultado[-4]
            total_taxas = resultado[-3]
            totaL_debitos = resultado[-2]
            total_repasses = resultado[-1]

            linha = f"""
            <tr>
                <td>{vendedor_id}</td>
                <td>{nome_vendedor}</td>
                <td>{valor_repasse_retido}</td>
            """
            for valor_dia in valores_diarios:
                linha += f"<td>{valor_dia}</td>"
            
            linha += f"""
            <td>{total_creditos}</td>
            <td>{total_taxas}</td>
            <td>{totaL_debitos}</td>
            <td>{total_repasses}</td>
            </tr>
            """
            tbody += linha

        context['tbody'] = tbody
        return render(request, 'home/tbl_bootstrap.html', context=context)
    return HttpResponse(" <h1>GET OR ANY REQUEST</h1> ")

def upload_planilha_quinzenal(request, *args, **kwargs):
    if request.method == 'POST':
        planilha = request.FILES.get('docpicker')
        #arquivo esta recebendo com sucesso, azer os devidos tratamentos
        return HttpResponse(planilha)
    return HttpResponseRedirect('/tbl_credito_cessao.html')

def download_planilha_quinzenal(request, *args, **kwargs):
    if request.session.get('serialized_data') is None:
        return HttpResponse('Nenhum dado encontrado para download')
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = os.path.join(tmpdir, f'planilha_consulta_quinzenal_{slugify(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))}.xlsx')
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet['A1'] = 'ID Vendedor'
        sheet['B1'] = 'Nome Vendedor'
        sheet['C1'] = 'Valor Repasse Retido'
        
        # define a largura das primeiras colunas
        sheet.column_dimensions[get_column_letter(1)].width = 15
        sheet.column_dimensions[get_column_letter(2)].width = 30
        sheet.column_dimensions[get_column_letter(3)].width = 30
        
        for i, row in enumerate(json.loads(request.session.get('serialized_data'))):
            for j, value in enumerate(row):
                sheet.cell(row=i+2, column=j+1, value=value)
        workbook.save(filepath)
        with open(filepath, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(filepath)}"'
            return response

def download_planilha_cob(request, *args, **kwargs):
    if request.session.get('serialized_data') is None:
        return HttpResponse('Nenhum dado encontrado para download')
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = os.path.join(tmpdir, f'planilha_consulta_cob_{slugify(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))}.xlsx')
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet['A1'] = 'ID Contrato'
        sheet['B1'] = 'Vendedor'
        sheet['C1'] = 'Comprador'
        sheet['D1'] = 'N Parcela'
        sheet['E1'] = 'Valor Parcela'
        sheet['F1'] = 'Valor Pago'
        sheet['G1'] = 'Data Vencimento'
        sheet['H1'] = 'Data Credito'
        sheet['I1'] = 'Data Procesamento'
        sheet['J1'] = 'Banco'
        sheet['K1'] = 'Parcela Paga'
        sheet['L1'] = 'Total Parcelas'
        sheet['M1'] = 'Total Quitadas'
        sheet['N1'] = 'Evento'
        sheet['O1'] = 'Produto'
        sheet['P1'] = 'Deposito'
        sheet['Q1'] = 'Calculo'
        sheet['R1'] = 'Taxas'
        sheet['S1'] = 'ADI'
        sheet['T1'] = 'ME'
        sheet['U1'] = 'OP'
        sheet['V1'] = 'Repasses'
        sheet['W1'] = 'Comissao'
        for i, row, in enumerate(json.loads(request.session.get('serialized_data'))):
            for j, value in enumerate(row):
                sheet.cell(row=i+2, column=j+1, value=value)
        workbook.save(filepath)
        with open(filepath, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(filepath)}"'
            return response

def upload_planilha_cob(request, *args, **kwargs):
    if request.method == 'POST':
        planilha = request.FILES.get('docpicker')
        #verificar se o arquivo é do tipo xlsx
        if planilha.name.endswith('.xlsx'):
            #arquivo esta recebendo com sucesso, azer os devidos tratamentos
            wb = openpyxl.load_workbook(planilha)
            #nesse arquivo de planilha, a primeira aba é a que contem os dados, e so existe uma aba
            sheet = wb.worksheets[0]
            linha = 0
            for row in sheet.iter_rows(values_only=True):
                if linha < 1:
                    linha += 1
                    continue
                linha += 1
                if (row[0] and row[1] and row[2]) == None:
                    break
            
            
        #arquivo esta recebendo com sucesso, azer os devidos tratamentos
        return HttpResponse(planilha)
    return HttpResponseRedirect('/form_elements.html')

def editar_boleto_avulso(request, *args, **kwargs):
    return HttpResponse("<h1>FUNCIONOU</h1>")

def upload_planilha_cavalos_cob(request, *args, **kwargs):
    if request.method == 'POST':
        planilha = request.FILES.get('docpicker')
        if planilha is None:
            return HttpResponse('Nenhum arquivo selecionado')
        elif planilha.name.endswith('.xlsx'):
            pessoa_nula = Pessoas.objects.get(id=99999)
            erros:list[str] = []
            linhas_nulas = 0
            wb = openpyxl.load_workbook(planilha)
            cob = wb.active
            linha = 0
            for row in cob.iter_rows(values_only=True):
                if linha < 1:
                    linha += 1
                    continue
                if (row[0] and row[1] and row[2]) == (None or ''):
                    linhas_nulas += 1
                    if linhas_nulas == 2:
                        break
                    continue
                #TODO: Substituir cada posição do row por uma variavel com um nome mais significativo
                try:
                    vendedor = Pessoas.objects.get(id=row[0])
                except Pessoas.DoesNotExist:
                    vendedor = Pessoas.objects.create(id=row[0], nome=row[2], email=f"{row[0]}_{row[2]}@gmail.com")
                except Pessoas.MultipleObjectsReturned:
                    erros.append(f"O vendedor {row[2]} possui mais de um cadastro. linha: {linha}")
                    continue
                try:
                    comprador = Pessoas.objects.get(nome=row[3])
                except Pessoas.DoesNotExist:
                    comprador = Pessoas.objects.create(nome=row[3], email=f"{row[3]}@gmail.com")
                except Pessoas.MultipleObjectsReturned or Exception as e:
                    erros.append(f"O comprador {row[3]} possui mais de um cadastro. linha: {linha}")
                    continue
                    
                if row[1] is not None and type(row[1]) == int:
                    if row[1] == 1:
                        eventos = Eventos.objects.create(nome=row[4], leiloeiro=pessoa_nula, dt_evento=date.today(), tipo="qualquer")
                        Contratos.objects.create(vendedor=vendedor, comprador=comprador, eventos=eventos, descricao=row[10], pessoas_id_inclusao=pessoa_nula)
                    else:
                        try:
                            contratos = Contratos.objects.get(id=row[1])
                            try:
                                eventos = Eventos.objects.get(id=contratos.eventos.id)
                                eventos.nome = row[11]
                                eventos.save()
                            except Eventos.DoesNotExist:
                                eventos = Eventos.objects.create(nome=row[11], leiloeiro=pessoa_nula)
                                eventos.save()
                            #TODO: Discutir com tiago se pode deixar o usuario alterar o vendedor e comprador do contrato e tambem os id's
                            contratos.descricao = row[10]
                            contratos.eventos = eventos
                        except Contratos.DoesNotExist:
                            eventos = Eventos.objects.create(nome=row[11], leiloeiro=Pessoas.objects.get(id=99999),
                                dt_evento=date.today(), tipo="qualquer")
                            contratos = Contratos.objects.create(id=row[1],
                                vendedor=vendedor, comprador=comprador,
                                descricao=row[10], eventos=eventos, pessoas_id_inclusao=pessoa_nula)
                            contratos.save()
                else:
                    erros.append(f"O contrato {row[1]} não existe para o comprador: {row[3]} e vendedor: {row[2]}. linha: {linha}")
                    continue
                    
                try:
                    contrato_parcelas = ContratoParcelas.objects.get(contratos=contratos, 
                        nu_parcela=int(str(row[5].split('/')[0][1:])))
                    contrato_parcelas.dt_vencimento = row[7]
                    contrato_parcelas.vl_parcela = row[6]
                    contrato_parcelas.dt_credito = row[8]
                    contrato_parcelas.save()
                except ContratoParcelas.DoesNotExist:
                    contrato_parcelas = ContratoParcelas.objects.create(
                        contratos=contratos, nu_parcela=int(str(row[5].split('/')[0][1:])),
                        dt_vencimento=row[7], vl_parcela=row[6], dt_credito=row[8]
                    )
                    contrato_parcelas.save()
                except ContratoParcelas.MultipleObjectsReturned:
                    erros.append(f"O contrato {contratos.id} possui mais de uma parcela com o numero {row[5]}. linha: {linha}")
                    #!chances muito poucas de acontecer, mas se acontecer, o sistema vai pegar o primeiro objeto
                    pass
                try:
                    calculo_repasse = Calculo_Repasse.objects.get(contrato_parcelas=contrato_parcelas)
                    calculo_repasse.deposito = row[12]
                    calculo_repasse.calculo = row[13]
                    calculo_repasse.taxas = row[14]
                    calculo_repasse.adi = row[15]
                    calculo_repasse.me = row[16]
                    calculo_repasse.op = row[17]
                    calculo_repasse.repasses = row[18]
                    calculo_repasse.comissao = row[19]
                    calculo_repasse.save()
                except Calculo_Repasse.DoesNotExist:
                    calculo_repasse = Calculo_Repasse.objects.create(contrato_parcelas=contrato_parcelas,
                        deposito=row[12], calculo=row[13], taxas=row[14], adi=row[15],
                        me=row[16], op=row[17], repasses=row[18], comissao=row[19]
                    )
                    calculo_repasse.save()
                    
                linha += 1
            return HttpResponse('Planilha de cavalos recebida com sucesso, erros: {}'.format(erros))
        else:
            return HttpResponse('Arquivo não é do tipo xlsx')

def upload_planilha_cad_clientes(request, *args, **kwargs):
    if request.method == 'POST':
        planilha = request.FILES.get('docpicker')
        if planilha is None:
            return HttpResponse('Nenhum arquivo selecionado')
        elif planilha.name.endswith('.xlsx'):
            wb = openpyxl.load_workbook(planilha)
            cad_cliente = wb.active
            linha = 0
            for row in cad_cliente.iter_rows(values_only=True):
                if linha < 1:
                    linha += 1
                    continue
                #* sistema de parada
                if (row[0]) == None:
                    break
                try:
                    pessoa = Pessoas.objects.get(id=row[2])
                    pessoa.nome = row[0]
                    pessoa.email = row[1]
                except Pessoas.DoesNotExist:
                    pessoa = Pessoas.objects.create(id=row[2], nome=row[0], email=row[1])
                except Pessoas.MultipleObjectsReturned:
                    pass
                pessoa.save()
                try:
                    cad_cliente = CadCliente.objects.get(vendedor=pessoa)
                    cad_cliente.sim = row[3]
                    cad_cliente.nao = row[4]
                    cad_cliente.operacional = row[5]
                    cad_cliente.tcc = row[6]
                    cad_cliente.honorarios = row[7]
                    cad_cliente.animal = row[8]
                    cad_cliente.evento = row[9]
                    cad_cliente.informar_repasse = row[10]
                except CadCliente.DoesNotExist:
                    cad_cliente = CadCliente.objects.create(vendedor=pessoa, sim=row[3], nao=row[4],
                        operacional=row[5], tcc=row[6], honorarios=row[7], animal=row[8],
                        evento=row[9], informar_repasse=row[10])
                except CadCliente.MultipleObjectsReturned:
                    pass
                cad_cliente.save()
                
            return HttpResponse('Planilha {} recebida com sucesso'.format(planilha.name))
        else:
            return HttpResponse('Arquivo não é do tipo xlsx')