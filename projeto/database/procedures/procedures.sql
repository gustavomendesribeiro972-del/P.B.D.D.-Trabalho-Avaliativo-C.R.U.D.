CREATE OR REPLACE PROCEDURE registrar_venda(
	p_numero_cupom VARCHAR,
	p_cliente_id INTEGER,
	p_funcionario_id INTEGER,
	p_subtotal NUMERIC,
	p_desconto NUMERIC,
	p_total NUMERIC,
	p_observacao VARCHAR
)
LANGUAGE plpgsql
AS $$
DECLARE
	v_cliente_existe BOOLEAN:= FALSE;
BEGIN
	IF p_cliente_id IS NOT NULL THEN
		SELECT EXISTS(SELECT 1 FROM cliente WHERE id_cliente = p_cliente_id) INTO v_cliente_existe;
		
		IF NOT v_cliente_existe THEN
			RAISE EXCEPTION 'ERR: O cliente informado (ID %) não foi encontrado no cadastro.', p_cliente_id;
		END IF;
	END IF;

	INSERT INTO venda (
		numero_cupom, cliente_id, funcionario_id, subtotal, desconto, total, status, observacao
		)
	VALUES (
		p_numero_cupom, p_cliente_id, p_funcionario_id, p_subtotal, p_desconto, p_total, 'CONCLUÍDA', p_observacao
		);

	IF p_cliente_id IS NOT NULL THEN
		INSERT INTO movimentacao_pontos (cliente_id, tipo, quantidade, origem, observacao)
		VALUES(
			p_cliente_id,
			'ENTRADA',
			fn_calcular_pontos_compra(p_total),
			'COMPRA',
			'Pontos ganhados na venda ' || p_numero_cupom
		);
	END IF;
END;
$$;

CREATE OR REPLACE PROCEDURE adicionar_item_venda(
	p_venda_id INTEGER,
	p_variacao_id INTEGER,
	p_quantidade INTEGER,
	p_preco_unitario NUMERIC,
	p_desconto_item NUMERIC
)
LANGUAGE plpgsql 
AS $$
DECLARE
	v_estoque_atual INTEGER;
	v_subtotal NUMERIC;
	v_funcionario_id INTEGER;
BEGIN
	SELECT quantidade_estoque
	INTO v_estoque_atual
	FROM produto_variacao
	WHERE id_variacao = p_variacao_id;

	IF v_estoque_atual < p_quantidade THEN
		RAISE EXCEPTION 'ERR: Não tem estoque suficiente para o produto de variação ID:%. Estoque atual:%. Solicitado:%',
			p_variacao_id, v_estoque_atual, p_quantidade;
	END IF;
	
	v_subtotal := (p_quantidade * p_preco_unitario) - p_desconto_item;

	INSERT INTO item_venda (
		venda_id, variacao_id, quantidade, preco_unitario, desconto_item, subtotal
	)
	VALUES(
		p_venda_id, p_variacao_id, p_quantidade, p_preco_unitario, p_desconto_item, v_subtotal
	);

	UPDATE produto_variacao
	SET quantidade_estoque = quantidade_estoque - p_quantidade
	WHERE id_variacao = p_variacao_id;

	SELECT funcionario_id
	INTO v_funcionario_id
	FROM venda
	WHERE id_venda = p_venda_id;

	INSERT INTO movimentacao_estoque(
		variacao_id, funcionario_id, venda_id, tipo, quantidade, motivo_obs, origem_ref
	)
	VALUES (
		p_variacao_id, v_funcionario_id, p_venda_id, 'SAIDA', -p_quantidade, 'Baixa automática via PDV', origem_ref
	);
END;
$$;

CREATE OR REPLACE PROCEDURE registrar_cliente(
	p_nome VARCHAR,
	p_cpf VARCHAR,
	p_email VARCHAR
)
LANGUAGE plpgsql
AS $$
BEGIN
	INSERT INTO cliente (nome, cpf, email)
	VALUES (p_nome, p_cpf, p_email);
END;
$$;

CREATE OR REPLACE PROCEDURE registra_funcionarios(
	p_nomeUsuario VARCHAR,
	p_nomeApelido VARCHAR,
	p_cpf VARCHAR,
	p_telefone VARCHAR,
	p_email VARCHAR,
	p_senha VARCHAR
)
LANGUAGE plpgsql
AS $$
DECLARE
	v_perfil_id INTEGER;
	v_funcionario_existe BOOLEAN := FALSE;
	v_cpf_limpo VARCHAR;
BEGIN
	v_cpf_limpo := REGEXP_REPLACE(p_cpf, '[^0-9]', '', 'g');
	
	SELECT EXISTS(
		SELECT 1 FROM funcionario
		WHERE LOWER(TRIM(nome_Usuario)) = LOWER(TRIM(p_nomeUsuario)) OR cpf = v_cpf_limpo
	) INTO v_funcionario_existe;

	IF v_funcionario_existe THEN -- v_funcionario_existe = TRUE
		RAISE EXCEPTION 'ERR: Este nome de usuário / CPF já existe nesta loja!';
	END IF;

	SELECT id_perfil
	INTO v_perfil_id
	FROM perfil
	WHERE LOWER(TRIM(nomeUsuario)) = LOWER(TRIM(p_nomeUsuario));

	IF v_perfil_id IS NULL THEN
		INSERT INTO perfil (nomeUsuario, descricao)
        VALUES (p_nomeUsuario, 'Perfil criado automaticamente no cadastro de funcionário')
        RETURNING id_perfil INTO v_perfil_id;
	END IF;
	
	INSERT INTO funcionario (perfil_id, nome_Usuario, nome_Apelido, cpf, telefone, email, senha)
	VALUES (v_perfil_id, p_nomeUsuario, p_nomeApelido, p_cpf, p_telefone, p_email, p_senha);
END;
$$;

SELECT*FROM funcionario
CALL registrar_cliente('YGONA MOURA', '12345678911', 'ygona@empresa.com')
CALL registra_funcionarios('gerente_vendas', 'Marcos Oliveira', '55544433322', '(11) 96666-5555', 'marcos@empresa.com', 'hash_senha_999');
CALL registrar_venda('teste23233577', 1, 2, 50.00, 5.00, 45.00, 'teste')
CALL adicionar_item_venda(1, 2, 1, 120.00, 23.00)