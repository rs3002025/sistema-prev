
import pandas as pd
import os
import re
from datetime import datetime

def parse_with_strategy(file_path, strategy):
    """Tenta analisar uma planilha com base numa estratégia específica."""
    header_row, col_map = strategy
    try:
        # Tenta ler a planilha com a linha de cabeçalho especificada
        df = pd.read_excel(file_path, header=header_row)

        # Limpa os nomes das colunas para facilitar a correspondência
        df.columns = [str(col).strip().lower().replace('\n', ' ') for col in df.columns]

        # Verifica se as colunas de origem do mapa existem no dataframe
        if not all(k in df.columns for k in col_map.keys()):
            return None

        # Seleciona e renomeia as colunas de acordo com o mapa
        df = df[list(col_map.keys())]
        df.rename(columns=col_map, inplace=True)

        # Limpeza e validação dos dados
        df['competencia'] = pd.to_datetime(df['competencia'], errors='coerce')
        df['fator'] = pd.to_numeric(df['fator'], errors='coerce')
        df.dropna(subset=['competencia', 'fator'], inplace=True)

        # Se o dataframe não estiver vazio após a limpeza, retorna-o
        if not df.empty:
            df['arquivo_origem'] = os.path.basename(file_path)
            return df

    except Exception:
        # Se qualquer erro ocorrer, a estratégia falhou
        return None
    return None

# --- Estratégias de Análise ---
# Cada estratégia é uma tupla: (linha_do_cabeçalho, dicionário_de_mapeamento)
# O dicionário mapeia {nome_original_coluna: nome_final}
strategies = [
    # Estratégia principal para arquivos mais recentes
    (9, {'competência': 'competencia', 'fator simplificado (multiplicar)': 'fator'}),
    # Variações comuns
    (7, {'mês': 'competencia', 'fator simplificado': 'fator'}),
    (6, {'mês': 'competencia', 'fator': 'fator'}),
    (9, {'competência': 'competencia', 'fator': 'fator'}),
    (6, {'competência': 'competencia', 'fator': 'fator'}),
    (7, {'competência': 'competencia', 'fator': 'fator'}),
    # Casos com nomes de coluna "Unnamed"
    (9, {'unnamed: 1': 'competencia', 'unnamed: 2': 'fator'}),
    (8, {'unnamed: 1': 'competencia', 'unnamed: 2': 'fator'}),
    (7, {'unnamed: 1': 'competencia', 'unnamed: 2': 'fator'}),
    # Estratégia para o padrão "MÊS" e "FATOR" em linhas diferentes
    (7, {'mês': 'competencia', 'fator': 'fator'}),
    (8, {'mês': 'competencia', 'fator simplificado (multiplicar)': 'fator'}),
]

# --- Execução Principal ---

input_folder = "planilhas"
output_file = "dados_consolidados.csv"
error_log_file = "processing_errors.log"

all_files = [f for f in os.listdir(input_folder) if f.endswith((".xlsx", ".xls"))]
all_dataframes = []
failed_files = []

print(f"Iniciando processamento de {len(all_files)} planilhas...")

for filename in all_files:
    file_path = os.path.join(input_folder, filename)
    print(f"Processando: {filename}...")

    success = False
    for strategy in strategies:
        result_df = parse_with_strategy(file_path, strategy)
        if result_df is not None:
            all_dataframes.append(result_df)
            print("   -> Sucesso com a estratégia.")
            success = True
            break # Pára na primeira estratégia que funcionar

    if not success:
        failed_files.append(filename)
        print("   -> Falha em todas as estratégias.")

if failed_files:
    with open(error_log_file, "w") as f:
        for name in failed_files:
            f.write(f"{name}\n")

if all_dataframes:
    final_df = pd.concat(all_dataframes, ignore_index=True)
    final_df.drop_duplicates(inplace=True)
    final_df.sort_values(by=['arquivo_origem', 'competencia'], inplace=True)
    final_df.to_csv(output_file, index=False, encoding='utf-8-sig')

    print("\n--- Processamento Concluído ---")
    print(f" -> {len(all_files) - len(failed_files)} planilhas processadas com sucesso.")
    print(f" -> {len(failed_files)} planilhas falharam (ver 'processing_errors.log').")
    print(f" -> Total de {len(final_df)} linhas únicas salvas em '{output_file}'.")
else:
    print("\nNenhuma planilha pôde ser processada com sucesso.")
