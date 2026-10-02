--visão dos estoques dos produtos:
CREATE OR REPLACE VIEW vw_geral_estoque_produtos AS
SELECT
	p.id_produto,
	pv.id_variacao,
	p.nome_produto,
	pv.sku_variacao,
	p.categoria_id,
	pv.quantidade_estoque AS estoque_disponivel,
	pv.estoque_minimo,
	pv.status,
	p.preco_custo AS custo_padrao,
	p.preco_venda_base AS custo_reajustado
FROM produto p 
INNER JOIN produto_variacao pv
	ON  p.id_produto = pv.produto_id;

CREATE OR REPLACE VIEW vw_estoque_critico AS
SELECT
	p.id_produto,
	p.nome_produto,
	pv.id_variacao,
	pv.sku_variacao,
	pv.tamanho,
	pv.cor,
	pv.codigo_barras,
	pv.quantidade_estoque AS estoque_atual,
	pv.estoque_minimo,
	(pv.estoque_minimo - pv.quantidade_estoque) AS necessidade_reposicao
FROM produto_variacao pv
JOIN produto p ON p.id_produto = pv.produto_id
WHERE pv.quantidade_estoque <= estoque_minimo AND pv.status = 'ATIVO';

CREATE OR REPLACE VIEW vw_resumo_caixa_diario AS
SELECT
	f.id_funcionario,
	f.nome_Apelido AS nome_operador,
	DATE(v.data_hora) AS data_venda,
	COUNT(v.id_venda) AS quantidade_vendas,
	SUM(v.subtotal) AS total_subtotal,
	SUM(v.desconto) AS total_descontos,
	SUM(v.total) AS total_faturado,
	ROUND(AVG(v.total), 2) AS ticket_medio
FROM venda v
JOIN funcionario f ON v.funcionario_id = f.id_funcionario
WHERE v.status = 'CONCLUÍDA' GROUP BY f.id_funcionario, f.nome_Apelido, DATE(v.data_hora);

SELECT * FROM vw_geral_estoque_produtos;
SELECT * FROM vw_estoque_critico;
SELECT * FROM vw_resumo_caixa_diario;

DROP VIEW vw_geral_estoque_produtos
