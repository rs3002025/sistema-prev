
import pandas as pd
import os
import re

def identify_target_files():
    """Identifica os nomes dos arquivos das planilhas de Jan/2015 a Out/2025."""
    try:
        with open("links.txt", "r") as f:
            urls = [line.strip() for line in f.readlines()]
    except FileNotFoundError:
        print("Erro: 'links.txt' não encontrado. Execute 'get_links.py' primeiro.")
        return []

    target_files = []
    # Itera de 2015 até 2025
    for year in range(2015, 2026):
        # Itera de Janeiro a Dezembro
        for month in range(1, 13):
            # Para em Outubro de 2025
            if year == 2025 and month > 10:
                break

            # Constrói padrões de busca para encontrar o arquivo do mês/ano
            # Ex: "01_2015", "janeiro_2015", "2015...01"
            month_str = f"{month:02d}"
            year_str = str(year)
            # Padrões mais robustos que procuram pelo ano e mês no URL
            pattern1 = f"/{year_str}.*_{month_str}"
            pattern2 = f"_{month_str}.*_{year_str}"
            pattern3 = f"/{month_str}.*{year_str}"

            found_url = None
            for url in urls:
                if re.search(pattern1, url, re.IGNORECASE) or \
                   re.search(pattern2, url, re.IGNORECASE) or \
                   re.search(pattern3, url, re.IGNORECASE):
                    found_url = url
                    break

            if found_url:
                target_files.append(os.path.basename(found_url))

    # Remove duplicatas e retorna a lista
    return sorted(list(set(target_files)))

def processar_planilha_com_ajuda(filepath):
    """Exibe as primeiras linhas e pede ajuda ao usuário para processar."""
    print("-" * 70)
    print(f"Analisando: {os.path.basename(filepath)}")

    try:
        df_preview = pd.read_excel(filepath, header=None)
        print("Pré-visualização (primeiras 15 linhas):")
        print(df_preview.head(15).to_string())
    except Exception as e:
        print(f"  -> Erro ao ler o arquivo: {e}")
        return None

    try:
        header_row_str = input("  -> Digite o número da linha do CABEÇALHO (começando em 0), ou 'p' para pular: ")
        if header_row_str.lower() == 'p':
            return "skipped"
        if not header_row_str.isdigit():
            print("  -> Entrada inválida. Pulando.")
            return None
        header_row = int(header_row_str)

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

        df_processed.dropna(how='all', inplace=True)
        df_processed['competencia'] = pd.to_datetime(df_processed['competencia'], errors='coerce')
        df_processed['fator'] = pd.to_numeric(df_processed['fator'], errors='coerce')
        df_processed.dropna(subset=['competencia', 'fator'], inplace=True)

        return df_processed

    except Exception as e:
        print(f"  -> Ocorreu um erro durante o processamento: {e}")
        return None

# --- Execução ---

input_folder = "planilhas"
output_folder = "processados_2015_2025"
os.makedirs(output_folder, exist_ok=True)

target_files = identify_target_files()
processed_count = 0

if not target_files:
    print("Nenhum arquivo alvo para o período 2015-2025 foi identificado.")
else:
    print(f"{len(target_files)} planilhas alvo identificadas para o período 2015-2025.")
    for filename in target_files:
        filepath = os.path.join(input_folder, filename)

        # Define o caminho do arquivo de saída
        output_path = os.path.join(output_folder, re.sub(r'\.xlsx?$', '.csv', filename))

        if os.path.exists(output_path):
            print(f"Já processado: {filename}")
            processed_count += 1
            continue

        result = processar_planilha_com_ajuda(filepath)

        if isinstance(result, pd.DataFrame) and not result.empty:
            result.to_csv(output_path, index=False, encoding='utf-8-sig')
            print(f"  -> Salvo com sucesso em '{output_path}'")
            processed_count += 1
        elif result == "skipped":
             print(f"  -> {filename} pulado pelo usuário.")
        else:
            print(f"  -> Falha no processamento de {filename}.")

print("\n--- Ferramenta de Análise Assistida Concluída ---")
print(f"{processed_count} de {len(target_files)} planilhas alvo foram processadas e salvas em '{output_folder}'.")
