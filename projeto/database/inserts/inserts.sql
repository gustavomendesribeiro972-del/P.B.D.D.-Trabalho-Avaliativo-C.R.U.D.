-- OS PERFIS
INSERT INTO perfil(nomeUsuario)
VALUES ('Agatha Málevola'),
	('Samuels Seniors');

-- TODAS AS PERMISSÕES
INSERT INTO permissao(nomePermissao, descricao)
VALUES ('CADASTRAR_PRODUTO', 'Permite cadastrar novos produtos e variações no estoque'),
	('FINALIZAR_VENDA', 'Permite operar o caixa e concluir vendas'),
	('GERENCIAR_USUARIOS', 'Acesso total apra cadastrar funcionários e alterar perfis');

-- AS PERMISSÕES DOS DOIS PERFIS
INSERT INTO perfil_permissao(id_permissao, id_perfil)
VALUES (1, 1),		------------------
	(2,1),			--AGATHA
	(3,1),	---------------------------
	(2,2);		--SAMUELS

-- FUNCIONARIO
INSERT INTO funcionario (perfil_id, nome_Usuario, nome_Apelido, cpf, telefone, email, senha_hash) VALUES
(1, 'agatha.malevola', 'Agatha', '12345678901', '11999990001', 'agatha@lojacore.com', 'hash_senha_123'),
(2, 'samuels.seniors', 'Samuels', '98765432100', '11999990002', 'samuels@lojacore.com', 'hash_senha_456');

-- CLIENTE
INSERT INTO cliente (nome, cpf, telefone, email, endereco, data_nascimento) VALUES
('Carlos Oliveira', '11122233344', '11988881111', 'carlos@email.com', 'Rua das Flores, 123 - SP', '1990-05-15'),
('Mariana Santos', '55566677788', '11988882222', 'mariana@email.com', 'Av. Central, 456 - SP', '1995-10-20');

-- MOVIMENTACAO_PONTOS
INSERT INTO movimentacao_pontos (cliente_id, tipo, quantidade, origem, observacao) VALUES
(1, 'ENTRADA', 100, 'COMPRA_INICIAL', 'Pontos gerados no cadastro'),
(2, 'ENTRADA', 50, 'PROMOCAO', 'Bônus de boas-vindas');

-- CATEGORIA
INSERT INTO categoria (nome, descricao) VALUES
('Roupas Masculinas', 'Vestuário masculino em geral'),
('Calçados', 'Sapatos, tênis e sandálias');

-- PRODUTO
INSERT INTO produto (categoria_id, codigo_interno, nome_produto, descricao_produto, marca, preco_custo, preco_venda_base) VALUES
(1, 'PROD-CAM-001', 'Camiseta Oversized Basic', 'Camiseta 100% algodão corte moderno', 'LojaCore Wear', 30.00, 79.90),
(2, 'PROD-TEN-002', 'Tênis Running Comfort', 'Tênis para caminhada e corrida leve', 'SportMaster', 90.00, 219.90);

-- PRODUTO_VARIACAO
INSERT INTO produto_variacao (produto_id, codigo_barras, sku_variacao, tamanho, cor, quantidade_estoque, estoque_minimo) VALUES
(1, '789123456001', 'CAM-OVR-BLK-M', 'M', 'Preto', 25, 5),
(1, '789123456002', 'CAM-OVR-BLK-G', 'G', 'Preto', 15, 5),
(2, '789123456003', 'TEN-RUN-BLU-41', '41', 'Azul', 10, 2),
(2, '789123456004', 'TEN-RUN-BLU-38', '38', 'Azul', 1, 2),
(2, '789123456005', 'TEN-RUN-BLU-36', '36', 'Azul', 0, 2);

-- HISTORICO_PRECO
INSERT INTO historico_preco (variacao_id, prc_custo_anterior, prc_custo_novo, prc_venda_anterior, prc_venda_novo, funcionario_id) VALUES
(1, 25.00, 30.00, 69.90, 79.90, 1);

-- VENDA
INSERT INTO venda (numero_cupom, cliente_id, funcionario_id, subtotal, desconto, total, status, observacao) VALUES
('CUPOM-2026-001', 1, 2, 159.80, 9.80, 150.00, 'CONCLUÍDA', 'Venda realizada no caixa 01'),
('CUPOM-2026-002', 2, 2, 219.90, 0.00, 219.90, 'CONCLUÍDA', 'Cliente pagou via PIX');

-- ITEM_VENDA
INSERT INTO item_venda (venda_id, variacao_id, quantidade, preco_unitario, desconto_item, subtotal) VALUES
(1, 1, 2, 79.90, 9.80, 150.00), -- 2x Camiseta M
(2, 3, 1, 219.90, 0.00, 219.90); -- 1x Tênis 41

-- PAGAMENTO_VENDA
INSERT INTO pagamento_venda (venda_id, forma_pagamento, valor) VALUES
(1, 'CARTAO_CREDITO', 150.00),
(2, 'PIX', 219.90);

-- MOVIMENTACAO_ESTOQUE
INSERT INTO movimentacao_estoque (variacao_id, funcionario_id, venda_id, tipo, quantidade, motivo_obs, origiem_ref) VALUES
(1, 2, 1, 'SAIDA', -2, 'Baixa por venda', 'CUPOM-2026-001'),
(3, 2, 2, 'SAIDA', -1, 'Baixa por venda', 'CUPOM-2026-002');

-- TROCA
INSERT INTO troca (venda_origem_id, cliente_id, funcionario_id, valor_total_troca, observacao) VALUES
(1, 1, 1, 79.90, 'Troca de tamanho de Camiseta (M por G)');

-- ITEM_TROCA
INSERT INTO item_troca (troca_id, variacao_id, tipo_movimento, quantidade, preco_unitario, subtotal) VALUES
(1, 1, 'ENTRADA', 1, 79.90, 79.90), -- Devolvendo a tamanho M
(1, 2, 'SAIDA', 1, 79.90, 79.90);    -- Levando a tamanho G
