
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

url = "https://www.gov.br/previdencia/pt-br/assuntos/previdencia-social/legislacao/indice-de-atualizacao-das-contribuicoes-para-calculo-do-salario-de-beneficio"
output_file = "links.txt"

try:
    response = requests.get(url, timeout=30)
    response.raise_for_status()
except requests.exceptions.RequestException as e:
    exit()

soup = BeautifulSoup(response.content, "html.parser")
links = soup.find_all("a", href=lambda href: href and (href.endswith(".xlsx") or href.endswith(".xls")))

if not links:
    exit()

with open(output_file, "w") as f:
    for link in links:
        file_url = urljoin(url, link["href"])
        f.write(f"{file_url}\n")
