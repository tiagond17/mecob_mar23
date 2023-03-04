# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
from datetime import datetime, date, timedelta
from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.shortcuts import render
from django.db import connection, connections
from django.db.models import Sum
from django.db.models.functions import TruncDay, Coalesce, ExtractDay

from django.db.models import F, Count, FloatField, Q


from .existing_models import Contratos, ContratoParcelas, Pessoas
from .forms import CAD_ClienteForm, Calculo_RepasseForm
from .models import Calculo_Repasse, CadCliente, Debito, Credito, Taxa


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
        elif load_template == 'tbl_bootstrap.html':
            if request.method == 'POST':
                pass
                """
                data_inicio = request.POST.get('data-inicio')  # 2022-08-01:str
                data_fim = request.POST.get('data-fim')  # 2022-08-21:str
                print(data_inicio, data_fim)
                
                with connection.cursor() as cursor:
                    cursor.execute("select vendedor_id, contratos.id, comprador_id, tp_contrato, status ,vl_boleto, vl_pago, vl_parcela, nu_parcelas, dados_arquivo_retorno.dt_credito, contrato_parcelas.dt_credito from dados_arquivo_retorno, contratos, contrato_parcelas where contrato_parcelas.dt_credito >= '{}' and contrato_parcelas.dt_credito <= '{}' limit 1000".format(data_inicio, data_fim))
                    result = cursor.fetchall()
                    context['sql'] = result """
            with connection.cursor() as cursor:
                #!Transformar em função, igual ao carregar_tabela_cob
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
                SUM(DISTINCT credito.vl_credito) as tt_creditos,
                SUM(DISTINCT taxas.taxas) as tt_taxas,
                SUM(DISTINCT debito.vl_debito) as tt_debitos,
                SUM(cr.repasses) 
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
                GROUP BY cliente_id
                ) AS credito ON credito.cliente_id = c.vendedor_id

                LEFT JOIN (
                SELECT cliente_id, SUM(vl_debito) AS vl_debito 
                FROM debito 
                GROUP BY cliente_id
                ) AS debito ON debito.cliente_id = c.vendedor_id
                LEFT JOIN taxas on taxas.cliente_id = c.vendedor_id
                WHERE
                cr.dt_credito BETWEEN '2022-09-01' AND '2022-09-14'
                GROUP BY
                c.vendedor_id, p.nome
                """)
                context['sql'] = cursor.fetchall()
                context['mes_consultado'] = "{}, consultado do dia {} ate {}".format(date(month=9, year=2022, day=1).month, date(year=2022,month=9, day=1), date(year=2022,month=9, day=15))
            #context['quinzena_result'] = Calculo_Repasse.objects.select_related('id_vendedor').filter()

        elif load_template == 'cad_clientes_table_bootstrap.html':
            context['cad_clientes'] = CadCliente.objects.all()
            
        elif load_template == 'tbl_julia_bootstrap.html':
            if request.method == 'POST':
                pass
            pass
        
            with connection.cursor() as cursor:
                cursor.execute("""
                            select SUM(vl_pago) as valor_pago, sum(me) as honorarios from calculo_repasse where dt_credito = "2022-09-26"
                        """)
                valores_totais_bradesco = cursor.fetchall()
                cursor.execute("""
                    select distinct comissao as comissionista, 
                    sum(vl_pago*0.05) as comissoes 
                    from calculo_repasse
                    where dt_credito = "2022-09-26" and comissao != " -"  and banco="UNICRED"
                    group by comissao;
                    """)
                comissoes = cursor.fetchall()
                cursor.execute("""
                    select id_contrato_id,
                    pessoas.nome,
                    CASE WHEN id_contrato_id > 12460 OR ISNULL(id_contrato_id) THEN 'UNICRED' ELSE 'BRADESCO' END as banco,
                    sum(vl_pago)
                    from calculo_repasse
                    left join contratos on contratos.id=id_contrato_id
                    left join pessoas on pessoas.id = contratos.vendedor_id
                    where dt_credito = "2022-09-26"
                    group by contratos.vendedor_id
                """)
                repasses = cursor.fetchall()

            context['comissoes'] = comissoes
            context['valores_totais_bradesco'] = valores_totais_bradesco
            context['repasses'] = repasses
            #*Para filtrar todos os repasses do banco unicred
            #*Calculo_Repasse.objects.filter(dt_credito="2022-09-26", banco="UNICRED")
        elif load_template == 'form_elements.html':
            if request.method == "POST":
                data_inicio = request.POST.get('data_inicio')  # 2022-08-01:str
                data_fim = request.POST.get('data_fim')  # 2022-08-21:str
                context['sql'] = preencher_tabela_cob(
                    data_inicio=data_inicio, data_fim=data_fim)
            context['form'] = Calculo_RepasseForm()
            #!context['cad_clientes'] = CadCliente.objects.all()

        elif load_template == 'tbl_credito_cessao.html':
            if request.method == "POST":
                pass
                context['nothing'] = None
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT distinct vendedor_id, nome , nu_parcelas, dt_contrato FROM contratos
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
                WHERE c.dt_creditado >= '2023-03-01' AND c.dt_creditado < '2023-04-01'
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
                WHERE c.dt_debitado >= '2023-03-01' AND c.dt_debitado < '2023-04-01'
                GROUP BY p.id, p.nome""")
                context['debitos'] = cursor.fetchall()
            context['taxas'] = Taxa.objects.filter(dt_taxa__range=('2022-03-01', '2023-03-02'), taxas__gt=0)

            
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
    #!repasse = valor - taxa - me
    #!calc = valor - taxa
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
        Debito.objects.create(
            cliente = pagador,
            vl_debito = valor,
            dt_debitado = data_credito,
            descricao = descricao,
        )
        Credito.objects.create(
            cliente = credor,
            vl_credito = valor,
            dt_creditado = data_credito,
            descricao = descricao,
        )
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
        Taxa.objects.create(
            cliente = cliente,
            tipo = tipo,
            descricao = descricao_taxa,
            taxas = taxas,
            dt_taxa = data_taxa
        )
        return HttpResponseRedirect('/tbl_credito_cessao.html')
    return HttpResponse("<h1>GET OR ANY REQUEST</h1>")