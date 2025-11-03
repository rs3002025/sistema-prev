
import pandas as pd
import os

# Pasta onde os arquivos CSV processados estão salvos
input_folder = "processados_2015_2025"
# Arquivo de saída final
output_file = "dados_completos_planilhas_2015_a_2025.csv"

if not os.path.isdir(input_folder):
    print(f"Erro: A pasta '{input_folder}' não foi encontrada.")
    print("Execute a 'ferramenta_assistida.py' primeiro.")
    exit()

# Lista todos os arquivos CSV na pasta de processados
csv_files = [f for f in os.listdir(input_folder) if f.endswith(".csv")]

if not csv_files:
    print("Nenhum arquivo CSV encontrado para consolidar.")
    exit()

print(f"Consolidando {len(csv_files)} arquivos da pasta '{input_folder}'...")

all_dataframes = []

for filename in csv_files:
    filepath = os.path.join(input_folder, filename)
    try:
        df = pd.read_csv(filepath)
        # Adiciona o nome do arquivo de origem, caso não tenha sido adicionado antes
        if 'arquivo_origem' not in df.columns:
            df['arquivo_origem'] = filename
        all_dataframes.append(df)
    except Exception as e:
        print(f"Erro ao ler '{filename}': {e}")

if not all_dataframes:
    print("Nenhum dado pôde ser lido para a consolidação.")
    exit()

final_df = pd.concat(all_dataframes, ignore_index=True)

# Garante que a coluna de competência está no formato correto
final_df['competencia'] = pd.to_datetime(final_df['competencia'], errors='coerce')

# Ordena os dados pela planilha de origem e depois pela data
final_df.sort_values(by=['arquivo_origem', 'competencia'], inplace=True)

# Remove duplicatas baseadas na competência e fator, mantendo a última ocorrência
final_df.drop_duplicates(subset=['competencia', 'fator'], keep='last', inplace=True)

final_df.to_csv(output_file, index=False, encoding='utf-8-sig')

print("\n--- Consolidação Concluída ---")
print(f"Total de {len(final_df)} linhas únicas salvas em '{output_file}'.")
