
import pandas as pd

# Nomes dos arquivos de entrada e saída
input_file = "dados_consolidados.csv"
output_file = "dados_2015_a_2025.csv"

print(f"Carregando dados de '{input_file}'...")

try:
    # Carrega o conjunto de dados completo
    df = pd.read_csv(input_file)

    # Garante que a coluna 'competencia' é do tipo datetime
    df['competencia'] = pd.to_datetime(df['competencia'], errors='coerce')

    # Remove linhas onde a data não pôde ser convertida
    df.dropna(subset=['competencia'], inplace=True)

    # Define o intervalo de datas desejado
    start_date = pd.to_datetime("2015-01-01")
    end_date = pd.to_datetime("2025-12-31")

    print(f"Filtrando dados entre {start_date.date()} e {end_date.date()}...")

    # Aplica o filtro de data
    df_filtrado = df[(df['competencia'] >= start_date) & (df['competencia'] <= end_date)]

    if df_filtrado.empty:
        print("Nenhum dado encontrado no intervalo de datas especificado.")
    else:
        # Salva o dataframe filtrado em um novo arquivo CSV
        df_filtrado.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"\nFiltro concluído com sucesso!")
        print(f"{len(df_filtrado)} linhas de dados salvas em '{output_file}'.")

except FileNotFoundError:
    print(f"Erro: O arquivo de entrada '{input_file}' não foi encontrado.")
except Exception as e:
    print(f"Ocorreu um erro inesperado: {e}")
