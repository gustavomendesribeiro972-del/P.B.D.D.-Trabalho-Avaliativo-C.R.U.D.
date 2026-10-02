CREATE OR REPLACE FUNCTION fn_status_produto(
	p_produto_id INTEGER
)
RETURNS VARCHAR
AS $$
DECLARE
	v_total_estoque INTEGER;
BEGIN
	SELECT COALESCE(SUM(quantidade_estoque), 0)
	INTO v_total_estoque
	FROM produto_variacao
	WHERE produto_id = p_produto_id AND status = 'ATIVO';

	IF v_total_estoque > 0 THEN
		RETURN 'DISPONIVEL';
	ELSE
		RETURN 'SEM ESTOQUE';
	END IF;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION fn_calcular_pontos_compra(
	p_pontos NUMERIC
)
RETURNS NUMERIC
AS $$
DECLARE
	--OBS: CONTINUAR

SELECT fn_status_produto(2)
