from django.db import connection

def preencher_tabela_cob(data_inicio, data_fim) -> str:
    result = f"""
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
        ORDER BY cp.dt_credito ASC, cp.nu_parcela ASC
    """
    return result
    
def carregar_tabela_quinzenal(data_inicio, data_fim):
        """
        SELECT
        c.vendedor_id,
        p.nome AS nome_vendedor,
        repasse_retido.vlr_rep_retido as valor_repasse_retido,
        cr.dt_credito,
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
        WHERE dt_creditado BETWEEN '2022-09-01' AND '2022-09-14'
        GROUP BY cliente_id
        )
        AS credito ON credito.cliente_id = c.vendedor_id

        LEFT JOIN (
        SELECT cliente_id, SUM(vl_debito) AS vl_debito 
        FROM debito
        WHERE dt_debitado BETWEEN '2022-09-01' AND '2022-09-14'
        GROUP BY cliente_id
        )
        AS debito ON debito.cliente_id = c.vendedor_id

        LEFT JOIN (
            SELECT cliente_id, SUM(taxas) as taxas
            FROM taxas
            WHERE dt_taxa BETWEEN '2022-09-01' AND '2022-09-14'
            GROUP BY cliente_id
        )
        as taxas on taxas.cliente_id = c.vendedor_id

        LEFT JOIN (
            SELECT cliente_id, SUM(vlr_rep_retido) as vlr_rep_retido
            from repasse_retido
            WHERE dt_rep_retido BETWEEN '2022-09-01' AND '2022-09-14'
            group by cliente_id
        ) 
        as repasse_retido on repasse_retido.cliente_id = c.vendedor_id
        WHERE
        cr.dt_credito BETWEEN '2022-09-01' AND '2022-09-14'
        GROUP BY
        c.vendedor_id, p.nome
    """