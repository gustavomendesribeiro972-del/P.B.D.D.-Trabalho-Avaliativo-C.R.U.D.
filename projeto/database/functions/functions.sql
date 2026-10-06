CREATE OR REPLACE FUNCTION fn_autenticar_funcionario(
	p_cpf VARCHAR,
	p_senha VARCHAR
)
RETURNS TABLE (
	id_funcionario INTEGER,
	nome_Usuario VARCHAR,
	nome_Apelido VARCHAR,
	nomeUsuario VARCHAR
)
LANGUAGE plpgsql
AS $$
BEGIN
	RETURN QUERY
	SELECT
		f.id_funcionario,
		f.nome_Usuario,
		COALESCE(p.nomeUsuario, 'SEM PERFIL') AS nome_Usuario
		FROM funcionario f
		LEFT JOIN perfil p on f.perfil_id = p.id_perfil
		WHERE f.cpf = p_cpf AND f.senha = p_senha;
END;
$$;

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
	p_pontos_total NUMERIC
)
RETURNS INTEGER
AS $$
DECLARE
	v_pontos INTEGER;
	v_fator_conversao NUMERIC := 10.00;
BEGIN
	IF p_pontos_total IS NULL OR p_pontos_total <= 0 THEN
		RETURN 0;
	END IF;

	--Aredondamento para baixo com o FLOOR:
	v_pontos := FLOOR(p_pontos_total / v_fator_conversao);
	RETURN v_pontos;
END;
$$
LANGUAGE plpgsql;

SELECT fn_autenticar_funcionario('55544433322', 'hash_senha_999')
SELECT fn_calcular_pontos_compra(59.90)
SELECT fn_status_produto(2)