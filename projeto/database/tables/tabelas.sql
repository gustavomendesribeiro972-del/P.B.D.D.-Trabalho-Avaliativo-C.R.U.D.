CREATE TABLE perfil(
	id_perfil SERIAL PRIMARY KEY,
	nomeUsuario VARCHAR(60)UNIQUE NOT NULL,
	descricao VARCHAR(400) DEFAULT 'Um logista da LojaCore'
);

CREATE TABLE permissao(
	id_permissao SERIAL PRIMARY KEY,
	nomePermissao VARCHAR(60)NOT NULL UNIQUE,
	descricao VARCHAR(400)NOT NULL
);

CREATE TABLE perfil_permissao(
	id_permissao INTEGER NOT NULL,
	id_perfil INTEGER NOT NULL,
	PRIMARY KEY (id_perfil, id_permissao),

	CONSTRAINT fk_permissao_id
		FOREIGN KEY (id_permissao)
		REFERENCES permissao(id_permissao)
		ON DELETE CASCADE,

	CONSTRAINT fk_perfil_id
		FOREIGN KEY (id_perfil)
		REFERENCES perfil(id_perfil)
		ON DELETE CASCADE
);




CREATE TABLE funcionario(
	id_funcionario SERIAL PRIMARY KEY,
	perfil_id INTEGER NOT NULL,
	nome_Usuario VARCHAR(100) UNIQUE NOT NULL,
	nome_Apelido VARCHAR(40) NOT NULL,
	cpf VARCHAR(11) UNIQUE NOT NULL,
	telefone VARCHAR(15) NOT NULL,
	email VARCHAR(254) UNIQUE NOT NULL,
	senha_hash VARCHAR(60) NOT NULL,
	status VARCHAR(30) NOT NULL DEFAULT 'ATIVO' 
		CHECK (status IN ('ATIVO', 'INATIVO', 'SUSPENSO')),
	criado_em TIMESTAMP NOT NULL DEFAULT now(),
	atualizado_em TIMESTAMP NOT NULL DEFAULT now(),

	CONSTRAINT fk_perfil_id
		FOREIGN KEY (perfil_id)
		REFERENCES perfil(id_perfil)
);



CREATE TABLE cliente(
	id_cliente SERIAL PRIMARY KEY,
	nome VARCHAR(100) NOT NULL,
	cpf VARCHAR(11) UNIQUE,
	telefone VARCHAR(15),
	email VARCHAR(254)UNIQUE,
	endereco VARCHAR(250),
	data_nascimento DATE,
	status VARCHAR(30) NOT NULL DEFAULT 'ATIVO',
	data_cadastro TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE movimentacao_pontos(
	id_mov_pontos SERIAL PRIMARY KEY,
	cliente_id INTEGER NOT NULL,
	tipo VARCHAR(20) NOT NULL CHECK (tipo IN ('ENTRADA', 'SAÍDA')),
	quantidade INTEGER NOT NULL CHECK (quantidade > 0),
	origem VARCHAR(60) NOT NULL,
	data_hora TIMESTAMP NOT NULL DEFAULT now(),
	observacao VARCHAR(120),

	CONSTRAINT fk_cliente_id
		FOREIGN KEY (cliente_id)
		REFERENCES cliente(id_cliente)
);

CREATE TABLE categoria(
	id_categoria SERIAL PRIMARY KEY,
	nome VARCHAR(60) UNIQUE NOT NULL,
	descricao VARCHAR(255)
);

CREATE TABLE produto(
	id_produto SERIAL PRIMARY KEY,
	categoria_id INTEGER NOT NULL,
	codigo_interno VARCHAR(100) UNIQUE NOT NULL,
	nome_produto VARCHAR(120)NOT NULL,
	descricao_produto TEXT,
	marca VARCHAR(100)NOT NULL,
	preco_custo NUMERIC(10, 2)NOT NULL
		CHECK (preco_custo >= 0),
	preco_venda_base NUMERIC(10, 2)NOT NULL
		CHECK (preco_venda_base >= 0),
	data_criacao TIMESTAMP NOT NULL DEFAULT now(),
	data_alteracao TIMESTAMP NOT NULL DEFAULT now(),

	CONSTRAINT fk_produto_categoria
		FOREIGN KEY (categoria_id)
		REFERENCES categoria(id_categoria)
);


CREATE TABLE produto_variacao(
	id_variacao SERIAL PRIMARY KEY,
	produto_id INTEGER NOT NULL,
	codigo_barras VARCHAR(50) UNIQUE,
	sku_variacao VARCHAR(100) UNIQUE NOT NULL,
	tamanho VARCHAR(20) NOT NULL,
	cor VARCHAR(40) NOT NULL,
	quantidade_estoque INTEGER NOT NULL DEFAULT 0
		CHECK (quantidade_estoque >= 0),
	estoque_minimo INTEGER NOT NULL DEFAULT 5
		CHECK (estoque_minimo >= 0),
	status VARCHAR(20) NOT NULL DEFAULT 'ATIVO'
		CHECK (status IN ('ATIVO', 'INATIVO')),

	CONSTRAINT fk_variacao_produto
		FOREIGN KEY (produto_id)
		REFERENCES produto(id_produto)
);

CREATE TABLE historico_preco(
	id_historico_preco SERIAL PRIMARY KEY,
	variacao_id INTEGER NOT NULL, --O produto
	prc_custo_anterior NUMERIC(10, 2) NOT NULL,
	prc_custo_novo NUMERIC(10, 2) NOT NULL,
	prc_venda_anterior NUMERIC(10, 2) NOT NULL,
	prc_venda_novo NUMERIC(10, 2) NOT NULL,
	data_alteracao TIMESTAMP NOT NULL DEFAULT now(),
	funcionario_id INTEGER NOT NULL,

	CONSTRAINT fk_historico_variacao
		FOREIGN KEY (variacao_id)
		REFERENCES produto_variacao(id_variacao),

	CONSTRAINT fk_historico_funcionario
		FOREIGN KEY (funcionario_id)
		REFERENCES funcionario(id_funcionario)
);

CREATE TABLE venda(
	id_venda SERIAL PRIMARY KEY,
	numero_cupom VARCHAR(20) UNIQUE NOT NULL,
	data_hora TIMESTAMP NOT NULL DEFAULT now(),
	cliente_id INTEGER,
	funcionario_id INTEGER NOT NULL,
	subtotal NUMERIC(10, 2)NOT NULL
		CHECK (subtotal >= 0),
	desconto NUMERIC(10, 2)NOT NULL DEFAULT 0.00
		CHECK (desconto >= 0),
	total NUMERIC(10, 2)NOT NULL
		CHECK (total >= 0),
	status VARCHAR(30)NOT NULL DEFAULT 'CONCLUÍDA'
		CHECK (status IN ('EM ANDAMENTO', 'CONCLUÍDA', 'CANCELADA')),
	observacao VARCHAR(120),

	CONSTRAINT fk_cliente_id
		FOREIGN KEY (cliente_id)
		REFERENCES cliente(id_cliente),

	CONSTRAINT fk_funcionario_id
		FOREIGN KEY (funcionario_id)
		REFERENCES funcionario(id_funcionario)
);

CREATE TABLE item_venda (
	id_item_venda SERIAL PRIMARY KEY,
	venda_id INTEGER NOT NULL,
	variacao_id INTEGER NOT NULL,
	quantidade INTEGER NOT NULL
		CHECK (quantidade > 0),
	preco_unitario NUMERIC(10, 2) NOT NULL
		CHECK (preco_unitario >= 0),
	desconto_item NUMERIC(10, 2) NOT NULL DEFAULT 0.00
		CHECK (desconto_item >= 0),
	subtotal NUMERIC(10, 2) NOT NULL
		CHECK (subtotal >= 0),

	CONSTRAINT fk_itens_da_venda
		FOREIGN KEY (venda_id)
		REFERENCES venda(id_venda),

	CONSTRAINT fk_itens_com_variacao
		FOREIGN KEY (variacao_id)
		REFERENCES produto_variacao(id_variacao)
);

CREATE TABLE pagamento_venda(
	id_pagamento SERIAL PRIMARY KEY,
	venda_id INTEGER NOT NULL,
	forma_pagamento VARCHAR(30) NOT NULL
		CHECK (forma_pagamento IN ('DINHEIRO', 'PIX', 'CARTAO_CREDITO', 'CARTAO_DEBITO', 'PONTOS_FIDELIDADE', 'OUTRO')),
	valor NUMERIC(10, 2) NOT NULL
		CHECK (valor > 0),
	data_hora TIMESTAMP NOT NULL DEFAULT now(),

	CONSTRAINT fk_pagamento_venda
		FOREIGN KEY (venda_id)
		REFERENCES venda(id_venda)
);



CREATE TABLE movimentacao_estoque (
	id_movimentacao SERIAL PRIMARY KEY,
	variacao_id INTEGER NOT NULL,
	funcionario_id INTEGER NOT NULL,
	venda_id INTEGER,
	tipo VARCHAR(20) NOT NULL
		CHECK (tipo IN ('ENTRADA', 'SAIDA', 'AJUSTE', 'DEVOLUCAO', 'TROCA')),
	quantidade INTEGER NOT NULL CHECK (quantidade != 0),
	data_hora TIMESTAMP NOT NULL DEFAULT now(),
	motivo_obs VARCHAR(255),
	origem_ref VARCHAR(100),

	CONSTRAINT fk_mov_estoq_variacao
		FOREIGN KEY (variacao_id)
		REFERENCES produto_variacao(id_variacao),

	CONSTRAINT fk_mov_estoq_funcionario
		FOREIGN KEY (funcionario_id)
		REFERENCES funcionario(id_funcionario),

	CONSTRAINT fk_mov_estoq_venda
		FOREIGN KEY (venda_id)
		REFERENCES venda(id_venda)
);

CREATE TABLE troca (
	id_troca SERIAL PRIMARY KEY,
	venda_origem_id INTEGER NOT NULL,
	cliente_id INTEGER,
	funcionario_id INTEGER NOT NULL,
	data_hora TIMESTAMP NOT NULL DEFAULT now(),
	valor_total_troca NUMERIC(10, 2) NOT NULL
		CHECK (valor_total_troca >= 0),
	observacao VARCHAR(255),

	CONSTRAINT fk_troca_venda
		FOREIGN KEY (venda_origem_id)
		REFERENCES venda(id_venda),

	CONSTRAINT fk_troca_cliente
		FOREIGN KEY (cliente_id)
		REFERENCES cliente(id_cliente),

	CONSTRAINT fk_troca_funcionario
		FOREIGN KEY (funcionario_id)
		REFERENCES funcionario(id_funcionario)
);

CREATE TABLE item_troca (
	id_item_troca SERIAL PRIMARY KEY,
	troca_id INTEGER NOT NULL,
	variacao_id INTEGER NOT NULL,
	tipo_movimento VARCHAR(10) NOT NULL
		CHECK (tipo_movimento IN ('ENTRADA', 'SAIDA')),
	quantidade INTEGER NOT NULL
		CHECK (quantidade > 0),
	preco_unitario NUMERIC(10, 2) NOT NULL
		CHECK (preco_unitario >= 0),
	subtotal NUMERIC(10, 2) NOT NULL
		CHECK (subtotal >= 0),

	CONSTRAINT fk_item_troca_cabecalho
		FOREIGN KEY (troca_id)
		REFERENCES troca(id_troca)
		ON DELETE CASCADE,

	CONSTRAINT fk_item_troca_variacao
		FOREIGN KEY (variacao_id)
		REFERENCES produto_variacao(id_variacao)
);
