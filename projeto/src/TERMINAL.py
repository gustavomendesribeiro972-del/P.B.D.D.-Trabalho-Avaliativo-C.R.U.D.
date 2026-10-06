#Aplicativo versão em terminal>:
import sys
import uuid
from conexao import testar_conexao, registrar_venda, listar_vendas_recentes


def menu():
    print("\n==========================================")
    print("      LOJACORE - TESTE DE BANCO (CLI)")
    print("==========================================")
    print("1 - Testar Conexão com o Banco")
    print("2 - Inserir Venda (CALL registrar_venda)")
    print("3 - Listar Últimas Vendas (SELECT)")
    print("0 - Sair")
    print("==========================================")


def cadastrar_venda_cli():
    print("\n--- NOVO REGISTRO DE VENDA ---")

    #Ajusta o cupom:
    cupom_sugerido = f"CUPOM-{uuid.uuid4().hex[:6].upper()}"
    cupom = input(f"Número do Cupom [{cupom_sugerido}]: ").strip()
    if not cupom:
        cupom = cupom_sugerido

    #Ajusta o clinte:
    cliente_input = input("ID do Cliente (Pressione ENTER para Cliente Anônimo/NULL): ").strip()
    cliente_id = int(cliente_input) if cliente_input.isdigit() else None

    #Ajusta o funcionario:
    func_input = input("ID do Funcionário [padrão 2]: ").strip()
    funcionario_id = int(func_input) if func_input.isdigit() else 2

    try:
        subtotal = float(input("Subtotal (ex: 100.00): ") or "100.00")
        desconto = float(input("Desconto (ex: 10.00): ") or "10.00")
        total = max(0.0, subtotal - desconto)
        print(f"-> Total Calculado: R$ {total:.2f}")
    except ValueError:
        print("Erro: Insira valores numéricos válidos!")
        return

    obs = input("Observação [Venda via Terminal]: ").strip() or "Venda via Terminal"

    sucesso, mensagem = registrar_venda(
        cupom, cliente_id, funcionario_id, subtotal, desconto, total, obs
    )
    
    if sucesso:
        print(f"\n {mensagem}")
    else:
        print(f"\n {mensagem}")


def exibir_vendas_cli():
    print("\n--- ÚLTIMAS VENDAS REGISTRADAS ---")
    vendas = listar_vendas_recentes()
    
    if not vendas:
        print("Nenhuma venda encontrada.")
        return

    print(f"{'ID':<5} | {'CUPOM':<15} | {'CLIENTE':<10} | {'FUNC.':<7} | {'TOTAL':<10} | {'STATUS':<10}")
    print("-" * 65)
    for v in vendas:
        cliente = str(v.cliente_id) if v.cliente_id is not None else "ANÔNIMO"
        print(f"{v.id_venda:<5} | {v.numero_cupom:<15} | {cliente:<10} | {v.funcionario_id:<7} | R$ {v.total:<7.2f} | {v.status:<10}")


def main():
    #Testa a conexão no inicio:
    ok, msg = testar_conexao()
    if not ok:
        print(f"{msg}")
        print("Verifique a string de conexão no arquivo conexao.py!")
        return

    print(f"{msg}")

    while True:
        menu()
        opcao = input("Escolha uma opção: ").strip()

        match opcao:
            case "1":
                ok, msg = testar_conexao()
                print(f"\nStatus: {msg}")
            case "2":
                cadastrar_venda_cli()
            case "3":
                exibir_vendas_cli()
            case "0":
                print("\nSaindo... Teste finalizado!")
                sys.exit()
            case _:
                print("\nOpção inválida, tente novamente.")


if __name__ == "__main__":
    main()