
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# URL do site
url = "https://www.gov.br/previdencia/pt-br/assuntos/previdencia-social/legislacao/indice-de-atualizacao-das-contribuicoes-para-calculo-do-salario-de-beneficio"

# Nome do arquivo de saída
output_file = "links.txt"

print("Iniciando a busca por links de planilhas...")

try:
    # Baixar o conteúdo da página com timeout
    response = requests.get(url, timeout=30)
    # Verificar se a requisição foi bem-sucedida
    response.raise_for_status()
except requests.exceptions.RequestException as e:
    print(f"Erro crítico ao acessar a página principal: {e}")
    exit()

# Analisar o HTML da página
soup = BeautifulSoup(response.content, "html.parser")

# Encontrar todos os links que terminam com .xlsx ou .xls
links = soup.find_all("a", href=lambda href: href and (href.endswith(".xlsx") or href.endswith(".xls")))

if not links:
    print("Nenhum link de planilha encontrado na página.")
    exit()

# Extrair os URLs completos e guardá-los
with open(output_file, "w") as f:
    for link in links:
        # Construir o URL absoluto a partir do link relativo
        file_url = urljoin(url, link["href"])
        f.write(f"{file_url}\n")

print(f"{len(links)} links foram extraídos e salvos em '{output_file}'.")
