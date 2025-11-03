
import pandas as pd
import os
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime

# --- Configuração ---
URL = "https://www.gov.br/previdencia/pt-br/assuntos/previdencia-social/legislacao/indice-de-atualizacao-das-contribuicoes-para-calculo-do-salario-de-beneficio"
ARQUIVO_PRINCIPAL = "dados_completos_automatico.csv"
PASTA_DOWNLOAD = "planilhas"

def encontrar_link_mais_recente():
    """Encontra o URL da planilha com a data mais recente no nome."""
    print("Buscando o link da planilha mais recente...")
    try:
        response = requests.get(URL, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        links = soup.find_all("a", href=lambda href: href and (href.endswith(".xlsx") or href.endswith(".xls")))

        link_mais_recente = None
        data_mais_recente = datetime(1900, 1, 1)

        for link in links:
            href = link.get('href', '')
            # Tenta extrair data no formato MM_YYYY ou MM-YYYY
            match = re.search(r'(\d{2})_(\d{4})|(\d{2})-(\d{4})', href)
            if match:
                groups = [g for g in match.groups() if g is not None]
                if len(groups) == 2:
                    month, year = int(groups[0]), int(groups[1])
                    data_atual = datetime(year, month, 1)

                    if data_atual > data_mais_recente:
                        data_mais_recente = data_atual
                        link_mais_recente = href

        if link_mais_recente:
            url_completa = urljoin(URL, link_mais_recente)
            print(f"Link mais recente encontrado: {url_completa}")
            return url_completa
        else:
            print("Não foi possível determinar o link mais recente.")
            return None
    except Exception as e:
        print(f"Erro ao buscar links: {e}")
        return None

def processar_planilha_nova(filepath):
    """Processa a nova planilha baixada com as regras fixas."""
    print(f"Processando '{os.path.basename(filepath)}'...")
    # Reutiliza a mesma lógica do processador_inteligente
    try:
        df_full = pd.read_excel(filepath, header=None)
        ref_month_str = str(df_full.iloc[4, 1])
        if 'nan' in ref_month_str.lower(): ref_month_str = str(df_full.iloc[4, 0])
        if 'nan' in ref_month_str.lower(): ref_month_str = str(df_full.iloc[4, 2])
        match = re.search(r'(\w+/\d{4})', ref_month_str)
        ref_month_str = match.group(1) if match else os.path.basename(filepath)

        df_data = pd.read_excel(filepath, header=None, skiprows=9, usecols=[1, 2])
        df_data.columns = ['competencia', 'fator']
        df_data['mes_referencia_planilha'] = ref_month_str
        df_data['arquivo_origem'] = os.path.basename(filepath)

        df_data.dropna(how='all', inplace=True)
        df_data['competencia'] = pd.to_datetime(df_data['competencia'], errors='coerce')
        df_data['fator'] = pd.to_numeric(df_data['fator'], errors='coerce')
        df_data.dropna(subset=['competencia', 'fator'], inplace=True)
        return df_data
    except Exception as e:
        print(f"   -> Erro ao processar a nova planilha: {e}")
        return None

# --- Execução Principal ---

novo_link = encontrar_link_mais_recente()

if novo_link:
    nome_arquivo_novo = os.path.basename(novo_link)
    caminho_arquivo_novo = os.path.join(PASTA_DOWNLOAD, nome_arquivo_novo)

    # 1. Baixar o novo arquivo
    print(f"Baixando '{nome_arquivo_novo}'...")
    try:
        os.makedirs(PASTA_DOWNLOAD, exist_ok=True)
        r = requests.get(novo_link, timeout=60)
        r.raise_for_status()
        with open(caminho_arquivo_novo, 'wb') as f:
            f.write(r.content)
    except Exception as e:
        print(f"Falha no download: {e}")
        exit()

    # 2. Processar o novo arquivo
    novos_dados_df = processar_planilha_nova(caminho_arquivo_novo)

    if novos_dados_df is not None:
        # 3. Carregar o arquivo principal existente
        if os.path.exists(ARQUIVO_PRINCIPAL):
            print(f"Carregando dados existentes de '{ARQUIVO_PRINCIPAL}'...")
            dados_antigos_df = pd.read_csv(ARQUIVO_PRINCIPAL)
            # Concatenar dados antigos e novos
            df_final = pd.concat([dados_antigos_df, novos_dados_df], ignore_index=True)
        else:
            print("Arquivo principal não encontrado. Criando um novo.")
            df_final = novos_dados_df

        # 4. Remover duplicatas e ordenar
        df_final['competencia'] = pd.to_datetime(df_final['competencia'])
        df_final.drop_duplicates(subset=['competencia', 'fator', 'mes_referencia_planilha'], keep='last', inplace=True)
        df_final.sort_values(by=['mes_referencia_planilha', 'competencia'], inplace=True)

        # 5. Salvar o arquivo atualizado
        df_final.to_csv(ARQUIVO_PRINCIPAL, index=False, encoding='utf-8-sig')
        print(f"\nSucesso! '{ARQUIVO_PRINCIPAL}' foi atualizado com {len(novos_dados_df)} novas linhas.")
        print(f"Total de linhas agora: {len(df_final)}.")
else:
    print("Nenhuma ação realizada.")
