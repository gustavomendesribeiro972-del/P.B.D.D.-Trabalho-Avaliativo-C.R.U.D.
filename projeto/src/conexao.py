#conexão:
from decimal import Decimal
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://postgres:root@localhost:5432/LojaCore"

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)


def testar_conexao():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True, "Conexão com b.d.d. efetuada com sucesso!"
    except Exception as e:
        return False, f"Falhana conexão: {e}"

#Views:
def vw_vendas_recentes():
    #Consulta a view 'vw_vendas_recentes'
    sessao = SessionLocal()
    try:
        query = text("SELECT * FROM vw_vendas_recentes")
        resultado = sessao.execute(query).fetchall()
        return resultado
    except Exception as e:
        print(f"Erro ao consultar as vendas: {e}")
        return []
    finally:
        sessao.close()

def vw_geral_estoque_produtos():
    sessao = SessionLocal()
    try:
        query = text("SELECT * FROM vw_geral_estoque_produtos")
        resultado = sessao.execute(query).fetchall()
        return resultado
    except Exception as e:
        print(f"Erro ao consultar o estoque: {e}")
        return []
    finally:
        sessao.close()

def vw_estoque_critico():
    sessao = SessionLocal()
    try:
        query = text("SELECT * FROM vw_estoque_critico")
        resultado = sessao.execute(query).fetchall()
        return resultado
    except Exception as e:
        print(f"Erro ao consultar o estoque: {e}")
        return []
    finally:
        sessao.close()

def vw_resumo_caixa_diario():
    sessao = SessionLocal()
    try:
        query = text("SELECT * FROM vw_resumo_caixa_diario")
        resultado = sessao.execute(query).fetchall()
        return resultado
    except Exception as e:
        print(f"Erro ao consultar o estoque: {e}")
        return []
    finally:
        sessao.close()

#Functions:
def fn_autenticar_funcionario(cpf, senha):
    with SessionLocal() as sessao:
        query = text(
            "SELECT fn_autenticar_funcionario(:p_cpf, :p_senha)"
        )

        resultado = sessao.execute(
            query,
            {"p_cpf": cpf, "p_senha": senha}
        )

        return resultado.scalar_one_or_none()


def fn_status_produto(produto_id):
    sessao = SessionLocal()

    try:
        query = text(
            "SELECT fn_status_produto(:p_produto_id);"
        )

        resultado = sessao.execute(
            query,
            {"p_produto_id": produto_id}
        )

        linha = resultado.fetchone()

        if linha is None:
            return None

        # Retorna o valor produzido pela função SQL.
        return linha[0]

    except Exception as e:
        print(f"Ocorreu um erro ao consultar o produto: {e}")
        raise

    finally:
        sessao.close()

def fn_calcular_pontos_compra(pontos_total):
    with SessionLocal() as sessao:
        try:
            query = text("""
                SELECT fn_calcular_pontos_compra(:p_valor)
            """)

            resultado = sessao.execute(
                query,
                {"p_valor": Decimal(str(pontos_total))}
            )

            return resultado.scalar_one_or_none()
        except Exception as e:
            print(f"Não foi possivel calcular os pontos: {e}")
        finally:
            sessao.close()

#Procedures:
def cadastrar_cliente(nome, cpf, email):
    with SessionLocal() as sessao:
        try:
            query = text("""
                CALL registrar_cliente(
                    CAST(:nome AS VARCHAR),
                    CAST(:cpf AS VARCHAR),
                    CAST(:email AS VARCHAR)
                )
            """)

            sessao.execute(query, {
                "nome": nome, 
                "cpf": cpf, 
                "email": email
                }
            )
            sessao.commit()
            return True, "Cliente cadastrado com sucesso!"
        except Exception as e:
            return False, f"Erro ao cadastrar cliente: {e}"
        finally:
            sessao.close()

def app_buscar_funcionario_por_cpf(cpf):
    try:
        with engine.connect() as conexao:
            resultado = conexao.execute(
                text("""
                    SELECT
                        id_funcionario AS funcionario_id,
                        cpf,
                        nome_usuario AS "nome_Usuario",
                        telefone,
                        email
                    FROM funcionario
                    WHERE cpf = :cpf
                """),
                {"cpf": cpf}
            )

            funcionario = resultado.mappings().first()

            return dict(funcionario) if funcionario else None

    except Exception as e:
        print(f"Erro ao buscar funcionário: {e}")
        return None

def registrar_funcionarios(
        nomeUsuario: str, 
        nomeApelido: str, 
        cpf: str, 
        telefone: str, 
        email: str, 
        senha: str
):
    sessao = SessionLocal()
    try:
        query = text ("""
            CALL registra_funcionarios(
                CAST(:nomeUsuario AS VARCHAR),
                CAST(:nomeApelido AS VARCHAR),
                CAST(:cpf AS VARCHAR),
                CAST(:telefone AS VARCHAR),
                CAST(:email AS VARCHAR),
                CAST(:senha AS VARCHAR)
            );
        """)

        sessao.execute(query, {
                "nomeUsuario": nomeUsuario,
                "nomeApelido": nomeApelido,
                "cpf":  cpf,
                "telefone": telefone,
                "email":    email,
                "senha":    senha
            }
        )

        sessao.commit()

        return True, "Funcionario registrado com sucesso!"
    
    except Exception as e:
        sessao.rollback()
        msg_erro = str(e).split("\n")[0]
        return False, f"Erro: {msg_erro}"
    
    finally:
        sessao.close()

def registrar_venda(cupom: str, cliente_id: int | None, funcionario_id: int, subtotal: float,
                    desconto: float, total: float, observacao: str):
    #Executa a procedure 'registrar_venda'
    sessao = SessionLocal()
    try:
        query = text("""
            CALL registrar_venda( 
                CAST(:cupom AS VARCHAR),
                CAST(:cliente AS INTEGER),
                CAST(:funcionario AS INTEGER), 
                CAST(:subtotal AS NUMERIC),
                CAST(:desconto AS NUMERIC),
                CAST(:total AS NUMERIC),
                CAST(:obs AS VARCHAR)
            );
        """)

        sessao.execute(query, {
                "cupom": str(cupom),
                "cliente": (int(cliente_id) if cliente_id is not None else None),
                "funcionario": int(funcionario_id),
                "subtotal": Decimal(str(subtotal)),
                "desconto": Decimal(str(desconto)),
                "total": Decimal(str(total)),
                "obs": str(observacao)
            }
        )
        sessao.commit()
        return True, "Venda registrada com sucesso!"
    except Exception as e:
        sessao.rollback()
        msg_erro = str(e).split("\n")[0]
        return False, f"Erro: {msg_erro}"
    finally:
        sessao.close()

def adicionar_item_venda(venda_id:int, variacao_id:int, quantidade:int, preco_unitario:float, desconto_item:float):
    sessao = SessionLocal()
    try:
        query = text("""
            CALL adicionar_item_venda(
                CAST(:venda_id AS INTEGER),
                CAST(:variacao_id AS INTEGER),
                CAST(:quantidade AS INTEGER),
                CAST(:preco_unitario AS NUMERIC),
                CAST(:desconto_item AS NUMERIC)
            );
        """)

        sessao.execute(query, {
            "venda_id": int(venda_id),
            "variacao_id": int(variacao_id),
            "quantidade": int(quantidade),
            "preco_unitario": float(preco_unitario),
            "desconto_item": float(desconto_item)
        })
        sessao.commit()
        return True, "Item adicionado numa venda"
    except Exception as e:
        return False, f"Erro: {e}"
    finally:
        sessao.close()
