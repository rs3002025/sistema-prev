
import pandas as pd
import re

# Nomes dos arquivos
input_file = "dados_completos_automatico.csv"
output_file = "dados_planilhas_2015_a_2025.csv"

print(f"Carregando dados de '{input_file}'...")

try:
    df = pd.read_csv(input_file)

    # Lista para guardar os nomes dos arquivos de origem que correspondem ao período
    arquivos_alvo = []

    # Pega a lista única de arquivos de origem
    arquivos_origem_unicos = df['arquivo_origem'].unique()

    # Itera de 2015 a 2025 para encontrar os arquivos correspondentes
    for ano in range(2015, 2026):
        ano_str = str(ano)
        for arquivo in arquivos_origem_unicos:
            # Procura o ano no nome do arquivo
            if ano_str in arquivo:
                arquivos_alvo.append(arquivo)

    # Remove duplicatas
    arquivos_alvo = list(set(arquivos_alvo))

    print(f"Encontrados {len(arquivos_alvo)} arquivos de planilha publicados entre 2015 e 2025.")

    # Filtra o dataframe principal para manter apenas as linhas dos arquivos alvo
    df_filtrado = df[df['arquivo_origem'].isin(arquivos_alvo)].copy()

    # Remove a coluna 'arquivo_origem' para a entrega final, se desejado
    # df_filtrado.drop(columns=['arquivo_origem'], inplace=True)

    if df_filtrado.empty:
        print("Nenhum dado encontrado para o período solicitado.")
    else:
        # Salva o resultado
        df_filtrado.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"\nFiltro concluído!")
        print(f"{len(df_filtrado)} linhas salvas em '{output_file}'.")

except FileNotFoundError:
    print(f"Erro: Arquivo '{input_file}' não encontrado.")
except Exception as e:
    print(f"Ocorreu um erro: {e}")
