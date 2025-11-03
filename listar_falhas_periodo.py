
import os
import re

def identify_target_files():
    """Identifica os nomes dos arquivos das planilhas de Jan/2015 a Out/2025."""
    try:
        with open("links.txt", "r") as f:
            urls = [line.strip() for line in f.readlines()]
    except FileNotFoundError:
        print("Erro: 'links.txt' não encontrado.")
        return []

    target_files = set()
    for year in range(2015, 2026):
        for month in range(1, 13):
            if year == 2025 and month > 10:
                break

            month_str = f"{month:02d}"
            year_str = str(year)

            # Padrões de busca melhorados
            patterns = [
                re.compile(f"_{month_str}_{year_str}"),
                re.compile(f"-{month_str}-{year_str}"),
                re.compile(f"/{year_str}/.*{month_str}"),
                re.compile(f"/{year_str}/.*{month:01d}"), # para meses sem zero à esquerda
            ]

            found_url = None
            for url in urls:
                # Extrai o nome do arquivo do URL para a correspondência
                filename_from_url = os.path.basename(url)
                # Tenta corresponder o ano e o mês de forma mais explícita
                if (year_str in filename_from_url) and (f"_{month_str}" in filename_from_url or f"-{month_str}" in filename_from_url or f".{month_str}" in filename_from_url):
                     # Regra especial para 2017, onde os nomes eram "benatual33a_17.09"
                    if year_str == '2017' and f".{month_str}" in filename_from_url:
                        target_files.add(filename_from_url)
                    elif year_str != '2017':
                         target_files.add(filename_from_url)

    return sorted(list(target_files))


# 1. Obter a lista de arquivos de planilhas que falharam
try:
    with open("processing_errors.log", "r") as f:
        failed_files = set(line.strip() for line in f)
except FileNotFoundError:
    print("Arquivo 'processing_errors.log' não encontrado.")
    failed_files = set()

# 2. Identificar todos os arquivos que pertencem ao período de 2015-2025
target_files = set(identify_target_files())

# 3. Encontrar a intersecção - arquivos que estão no período E falharam
failed_target_files = sorted(list(target_files.intersection(failed_files)))

if not failed_target_files:
    print("Boa notícia: Nenhuma das planilhas do período de 2015 a 2025 falhou no processamento.")
else:
    print("As seguintes planilhas do período 2015-2025 falharam no processamento automático:")
    for filename in failed_target_files:
        print(f"- {filename}")
