
import pandas as pd

# Nomes dos arquivos de entrada e saída
input_file = "dados_consolidados.csv"
output_file = "dados_2015_a_2025.csv"

print(f"Carregando dados de '{input_file}'...")

try:
    df = pd.read_csv(input_file)
    df['competencia'] = pd.to_datetime(df['competencia'], errors='coerce')
    df.dropna(subset=['competencia'], inplace=True)

    # A lógica correta: filtrar as PLANILHAS de origem, não as linhas.
    # O nome do arquivo de origem contém o ano.

    arquivos_alvo = set()
    for ano in range(2015, 2026):
        ano_str = str(ano)
        for arquivo in df['arquivo_origem'].unique():
            if ano_str in arquivo:
                arquivos_alvo.add(arquivo)

    print(f"Encontrados {len(arquivos_alvo)} arquivos de planilha cujo nome contém os anos de 2015 a 2025.")

    # Filtra o dataframe para manter apenas as linhas dos arquivos de planilha alvo.
    df_filtrado = df[df['arquivo_origem'].isin(arquivos_alvo)]

    if df_filtrado.empty:
        print("Nenhum dado encontrado de planilhas no intervalo de anos especificado.")
    else:
        df_filtrado.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"\nFiltro por planilha de origem concluído!")
        print(f"{len(df_filtrado)} linhas salvas em '{output_file}'.")

except FileNotFoundError:
    print(f"Erro: O arquivo de entrada '{input_file}' não foi encontrado.")
except Exception as e:
    print(f"Ocorreu um erro inesperado: {e}")
