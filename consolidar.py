
import pandas as pd
import os

# Pasta onde os arquivos CSV processados estão salvos
input_folder = "processados"
# Arquivo de saída final
output_file = "dados_consolidados.csv"

if not os.path.isdir(input_folder):
    print(f"Erro: A pasta '{input_folder}' não foi encontrada.")
    exit()

# Lista todos os arquivos CSV na pasta de processados
csv_files = [f for f in os.listdir(input_folder) if f.endswith(".csv")]

if not csv_files:
    print("Nenhum arquivo CSV encontrado para consolidar.")
    exit()

print(f"Consolidando {len(csv_files)} arquivos...")

# Lista para armazenar todos os dataframes
all_dataframes = []

for filename in csv_files:
    filepath = os.path.join(input_folder, filename)
    try:
        df = pd.read_csv(filepath)
        all_dataframes.append(df)
    except Exception as e:
        print(f"Erro ao ler '{filename}': {e}")

if not all_dataframes:
    print("Nenhum dado pôde ser lido para a consolidação.")
    exit()

# Concatena todos os dataframes em um único
final_df = pd.concat(all_dataframes, ignore_index=True)

# Remove duplicatas, mantendo a última ocorrência
final_df.drop_duplicates(inplace=True)

# Ordena os dados por competência
final_df.sort_values(by='competencia', inplace=True)

# Salva o arquivo consolidado
final_df.to_csv(output_file, index=False, encoding='utf-8-sig')

print("\nConsolidação concluída!")
print(f"Total de {len(final_df)} linhas únicas salvas em '{output_file}'.")
