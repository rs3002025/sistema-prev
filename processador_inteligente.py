
import pandas as pd
import os
import re

def processar_planilha_com_regras_fixas(filepath):
    """
    Processa uma planilha usando as regras fixas fornecidas pelo usuário:
    - Mês de referência está em B5.
    - Os dados começam em B10 (competência) e C10 (fator).
    """
    try:
        # Lê a planilha inteira sem cabeçalho para acessar células específicas
        df_full = pd.read_excel(filepath, header=None)

        # Extrai o mês de referência da célula B5 (índice 4, 1)
        # Às vezes, o valor pode estar em A5 ou C5 se mesclado
        ref_month_str = str(df_full.iloc[4, 1]) # B5
        if 'nan' in ref_month_str.lower():
             ref_month_str = str(df_full.iloc[4, 0]) # Tenta A5
        if 'nan' in ref_month_str.lower():
             ref_month_str = str(df_full.iloc[4, 2]) # Tenta C5

        # Pega a parte relevante do texto
        match = re.search(r'(\w+/\d{4})', ref_month_str)
        if match:
            ref_month_str = match.group(1)
        else:
            ref_month_str = os.path.basename(filepath) # Usa o nome do arquivo como fallback

        # Define a partir de qual linha ler os dados (linha 10, que é índice 9)
        # e quais colunas usar (B e C, que são índices 1 e 2)
        df_data = pd.read_excel(filepath, header=None, skiprows=9, usecols=[1, 2])

        # Define os nomes das colunas manualmente
        df_data.columns = ['competencia', 'fator']

        # Adiciona a coluna com o mês de referência
        df_data['mes_referencia_planilha'] = ref_month_str
        df_data['arquivo_origem'] = os.path.basename(filepath)

        # Limpeza final dos dados
        df_data.dropna(how='all', inplace=True)
        df_data['competencia'] = pd.to_datetime(df_data['competencia'], errors='coerce')
        df_data['fator'] = pd.to_numeric(df_data['fator'], errors='coerce')
        df_data.dropna(subset=['competencia', 'fator'], inplace=True)

        return df_data

    except Exception as e:
        print(f"   -> Erro ao processar {os.path.basename(filepath)}: {e}")
        return None

# --- Execução Principal ---

input_folder = "planilhas"
output_file = "dados_completos_automatico.csv"
error_log_file = "erros_processamento_final.log"

# Garante que a pasta de planilhas existe
if not os.path.isdir(input_folder):
    print(f"Erro: Pasta '{input_folder}' não encontrada. Execute o download primeiro.")
    exit()

all_files = [f for f in os.listdir(input_folder) if f.endswith((".xlsx", ".xls"))]
all_dataframes = []
failed_files = []

print(f"Iniciando processamento de {len(all_files)} planilhas com regras fixas...")

for filename in all_files:
    file_path = os.path.join(input_folder, filename)

    result_df = processar_planilha_com_regras_fixas(file_path)

    if result_df is not None and not result_df.empty:
        all_dataframes.append(result_df)
    else:
        failed_files.append(filename)

# Log de falhas
if failed_files:
    with open(error_log_file, "w") as f:
        for name in sorted(failed_files):
            f.write(f"{name}\n")

# Consolidação e salvamento
if all_dataframes:
    final_df = pd.concat(all_dataframes, ignore_index=True)
    final_df.sort_values(by=['mes_referencia_planilha', 'competencia'], inplace=True)
    final_df.to_csv(output_file, index=False, encoding='utf-8-sig')

    print("\n--- Processamento Concluído ---")
    print(f" -> {len(all_files) - len(failed_files)} de {len(all_files)} planilhas processadas com sucesso!")
    if failed_files:
        print(f" -> {len(failed_files)} planilhas falharam (ver '{error_log_file}').")
    print(f" -> Total de {len(final_df)} linhas salvas em '{output_file}'.")
else:
    print("\nNenhuma planilha pôde ser processada com sucesso.")
