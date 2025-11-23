import json
from src.Diary import DiaryAnalyzer
import time
#API Mudar para st.secrets
from segredos.watson_api import project_id

def print_menu():
    print("\n========================================")
    print("      GRANITE DIARY ANALYZER  (CLI)     ")
    print("========================================\n")
    print("1 → Processar UMA página (string manual)")
    print("2 → Processar arquivo .txt da pasta database/")
    print("3 → Processar TODAS as páginas da pasta database/")
    print("4 → Buscar documento no Firebase")
    print("5 → Consultar coleção do Firebase com filtro")
    print("6 → Listar TUDO de uma coleção")
    print("0 → Sair\n")


def escolher_backend():
    print("\nSelecione o backend:")
    print("1 → Local (Transformers + GPU)")
    print("2 → Watsonx.ai")
    escolha = input("Backend: ").strip()

    if escolha == "1":
        return "local"
    elif escolha == "2":
        return "watsonx"
    else:
        print("Opção inválida, usando default = local")
        return "local"


def main():
    #a chave está em segredos/apikey.json devo puxar o campo apikey
    #API Mudar para st.secrets
    with open("segredos/apikey.json", "r") as f:
        apikey_data = json.load(f)
    backend = escolher_backend()

    print("\nInicializando DiaryAnalyzer...\n")

    an = DiaryAnalyzer(
        backend=backend,
        watsonx_api_key= apikey_data["apikey"],
        watsonx_project_id=project_id
    )


    while True:
        print_menu()
        op = input("Escolha: ").strip()

        # ==========================================================
        # 1 → Processar texto digitado
        # ==========================================================
        if op == "1":
            texto = input("\nDigite o texto da página:\n> ")
            result = an.run_single_page(texto, page_name=f"pagina_manual_{int(time.time())}")

            print("\n🔍 Resultado do Granite:")
            print(json.dumps(result, indent=4, ensure_ascii=False))

        # ==========================================================
        # 2 → Processar arquivo .txt específico
        # ==========================================================
        elif op == "2":
            nome = input("Nome do arquivo (ex: pagina1.txt): ").strip()
            try:
                with open(f"database/{nome}", "r", encoding="utf-8") as f:
                    texto = f.read()

                result = an.run_single_page(texto, page_name=nome)
                print(json.dumps(result, indent=4, ensure_ascii=False))

            except FileNotFoundError:
                print("❌ Arquivo não encontrado em database/")

        # ==========================================================
        # 3 → Processar todas as páginas
        # ==========================================================
        elif op == "3":
            print("\nProcessando tudo em database/ ...")
            an.run()  # pipeline completo
            print("\n✔ Concluído! Veja a pasta results/")

        # ==========================================================
        # 4 → Buscar documento no Firebase
        # ==========================================================
        elif op == "4":
            col = input("Coleção: ").strip()
            doc = input("ID do documento: ").strip()
            resultado = an.get_document(col, doc)
            print(resultado)

        # ==========================================================
        # 5 → Query com filtro
        # ==========================================================
        elif op == "5":
            col = input("Coleção: ").strip()
            campo = input("Campo: ").strip()
            op_filtro = input("Operador (==, >=, <=, >, <): ").strip()
            valor = input("Valor: ").strip()

            # tentar converter para número quando possível
            try:
                valor = int(valor)
            except:
                pass

            resultados = an.query_collection(col, campo, op_filtro, valor)
            print(json.dumps(resultados, indent=4, ensure_ascii=False))

        # ==========================================================
        # 6 → Listar coleção inteira
        # ==========================================================
        elif op == "6":
            col = input("Coleção: ").strip()
            resultado = an.list_all(col)
            print(json.dumps(resultado, indent=4, ensure_ascii=False))

        # ==========================================================
        # SAIR
        # ==========================================================
        elif op == "0":
            print("Encerrando...")
            break

        else:
            print("Opção inválida.")


if __name__ == "__main__":
    main()
