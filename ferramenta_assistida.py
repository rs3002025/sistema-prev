
import pandas as pd
import os

def processar_planilha_com_ajuda(filepath):
    """Exibe as primeiras linhas e pede ajuda ao usuário para processar."""
    print("-" * 50)
    print(f"Analisando: {os.path.basename(filepath)}")

    try:
        df_preview = pd.read_excel(filepath, header=None)
        print("Pré-visualização (primeiras 15 linhas):")
        print(df_preview.head(15).to_string())
    except Exception as e:
        print(f"  -> Erro ao ler o arquivo: {e}")
        return None

    try:
        header_row = input("  -> Digite o número da linha do cabeçalho (começando em 0): ")
        if not header_row.isdigit():
            print("  -> Entrada inválida. Pulando.")
            return None
        header_row = int(header_row)

        df = pd.read_excel(filepath, header=header_row)
        df.columns = [str(col).strip() for col in df.columns]

        print("\n  Colunas disponíveis:", df.columns.tolist())
        competencia_col = input("  -> Copie e cole o nome da coluna de COMPETÊNCIA: ")
        fator_col = input("  -> Copie e cole o nome da coluna de FATOR: ")

        if competencia_col not in df.columns or fator_col not in df.columns:
            print("  -> Nomes de coluna inválidos. Pulando.")
            return None

        df_processed = df[[competencia_col, fator_col]].copy()
        df_processed.rename(columns={competencia_col: 'competencia', fator_col: 'fator'}, inplace=True)

        # Limpeza final
        df_processed['competencia'] = pd.to_datetime(df_processed['competencia'], errors='coerce')
        df_processed['fator'] = pd.to_numeric(df_processed['fator'], errors='coerce')
        df_processed.dropna(subset=['competencia', 'fator'], inplace=True)

        return df_processed

    except Exception as e:
        print(f"  -> Ocorreu um erro durante o processamento: {e}")
        return None

# --- Execução ---

input_folder = "planilhas"
output_folder = "processados"
os.makedirs(output_folder, exist_ok=True)

error_log_file = "processing_errors.log"
files_to_process = []

if os.path.exists(error_log_file):
    with open(error_log_file, "r") as f:
        files_to_process = [line.strip() for line in f if line.strip()]
    print(f"Processando {len(files_to_process)} arquivos que falharam anteriormente.")
else:
    files_to_process = [f for f in os.listdir(input_folder) if f.endswith((".xls", ".xlsx"))]
    print(f"Iniciando processamento de todos os {len(files_to_process)} arquivos.")

for filename in files_to_process:
    filepath = os.path.join(input_folder, filename)

    # Pular se já foi processado
    if os.path.exists(os.path.join(output_folder, f"{filename}.csv")):
        continue

    df_final = processar_planilha_com_ajuda(filepath)

    if df_final is not None and not df_final.empty:
        output_path = os.path.join(output_folder, f"{filename}.csv")
        df_final.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"  -> Salvo com sucesso em '{output_path}'")
    else:
        print("  -> Falha no processamento. O arquivo foi pulado.")

print("\nFerramenta de análise assistida concluída.")
