from django.db import connection

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