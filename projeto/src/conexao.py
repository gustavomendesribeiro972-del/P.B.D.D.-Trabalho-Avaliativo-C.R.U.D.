#conexão:
from decimal import Decimal
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://postgres:root@localhost:5432/LojaCore"

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind = engine)

def testar_conexao():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True, "Conexão com b.d.d. efetuada com sucesso!"
    except Exception as e:
        return False, f"Falhana conexão: {e}"

def registrar_venda(cupom: str, cliente_id: int | None, funcionario_id: int, subtotal: float,
                    desconto: float, total: float, observacao: str):
    #Executa a procedure 'registrar_venda'
    sessao = SessionLocal()
    try:
        stmt = text("""
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

        sessao.execute(stmt, {
                "cupom": str(cupom),
                "cliente": (int(cliente_id) if cliente_id is not None else None),
                "funcionario": int(funcionario_id),
                "subtotal": Decimal(str(subtotal)),
                "desconto": Decimal(str(desconto)),
                "total": Decimal(str(total)),
                "obs": str(observacao),
            },
        )
        sessao.commit()
        return True, "Venda registrada com sucesso!"
    except Exception as e:
        sessao.rollback()
        msg_erro = str(e).split("\n")[0]
        return False, f"Erro: {msg_erro}"
    finally:
        sessao.close()

def listar_vendas_recentes():
    #Consulta a view 'vw_vendas_recentes'
    sessao = SessionLocal()
    try:
        stmt = text("SELECT * FROM vw_vendas_recentes")
        resultado = sessao.execute(stmt).fetchall()
        return resultado
    except Exception as e:
        print(f"Erro ao consultar as vendas: {e}")
        return []
    finally:
        sessao.close()
