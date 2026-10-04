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
	DATE(ve.data_hora) AS data_venda,
	COUNT(ve.id_venda) AS quantidade_vendas,
	SUM(ve.subtotal) AS total_subtotal,
	SUM(ve.desconto) AS total_descontos,
	SUM(ve.total) AS total_faturado,
	ROUND(AVG(ve.total), 2) AS ticket_medio
FROM venda ve
JOIN funcionario f ON v.funcionario_id = f.id_funcionario
WHERE ve.status = 'CONCLUÍDA' GROUP BY f.id_funcionario, f.nome_Apelido, DATE(ve.data_hora);

CREATE OR REPLACE VIEW vw_vendas_recentes AS
SELECT 
	ve.id_venda, 
	ve.numero_cupom, 
	ve.cliente_id, 
	ve.funcionario_id,
	f.nome_Apelido AS nome_operador, 
	ve.total, 
	ve.status, 
	ve.data_hora
FROM venda ve 
JOIN funcionario f ON ve.funcionario_id = f.id_funcionario
ORDER BY id_venda DESC
LIMIT 10;

SELECT * FROM vw_vendas_recentes;
SELECT * FROM vw_geral_estoque_produtos;
SELECT * FROM vw_estoque_critico;
SELECT * FROM vw_resumo_caixa_diario;
