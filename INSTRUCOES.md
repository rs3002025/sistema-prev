
# Como Extrair os Dados Completos de 2015 a 2025

Este guia explica como usar as ferramentas para extrair os dados de **todas** as planilhas publicadas entre Janeiro de 2015 e Outubro de 2025.

**É crucial seguir estes passos na ordem correta.**

---

### Passo 1: Instalar as Dependências (se ainda não o fez)

Abra um terminal e execute o seguinte comando para instalar as bibliotecas Python necessárias:

```bash
pip install requests beautifulsoup4 pandas openpyxl xlrd
```

---

### Passo 2: Obter os Links das Planilhas

Este script vai varrer o site da Previdência e criar um ficheiro (`links.txt`) com o URL de cada planilha disponível.

```bash
python get_links.py
```

---

### Passo 3: Baixar Todas as Planilhas

Use o comando abaixo para baixar todas as planilhas listadas no `links.txt` para uma nova pasta chamada `planilhas`.

```bash
mkdir -p planilhas && cat links.txt | xargs wget -P planilhas/
```

---

### Passo 4: Processamento Assistido (O Passo Mais Importante)

Agora, vai executar a ferramenta interativa. Ela irá focar-se apenas nas ~130 planilhas do período que lhe interessa. Para cada uma, terá de a ajudar a encontrar os dados.

**Execute o script:**
```bash
python ferramenta_assistida.py
```

**Como funciona:**
1.  O script irá mostrar as primeiras 15 linhas de uma planilha.
2.  **Primeira Pergunta:** `Digite o número da linha que contém o CABEÇALHO`. Olhe para a pré-visualização e insira o número da linha onde os nomes das colunas (ex: "Competência", "Fator") aparecem. A contagem começa em 0.
3.  **Segunda Pergunta:** `Copie e cole o nome da coluna de COMPETÊNCIA`. O script mostrará uma lista de colunas que encontrou. Copie exatamente o nome da coluna que corresponde às datas/meses e cole-o no terminal.
4.  **Terceira Pergunta:** `Copie e cole o nome da coluna de FATOR`. Faça o mesmo para a coluna que contém os fatores numéricos.

O script irá então extrair os dados, limpá-los e guardá-los num ficheiro CSV individual na pasta `processados_2015_2025`.

**Se cometer um erro ou uma planilha for muito confusa, pode simplesmente premir Enter ou digitar 'p' para pular o ficheiro.**

---

### Passo 5: Consolidar o Resultado Final

Depois de ter processado todas as planilhas com a ferramenta assistida, execute este último script.

```bash
python consolidar.py
```

Ele irá juntar todos os pequenos ficheiros CSV da pasta `processados_2015_2025` num único grande ficheiro de dados, chamado `dados_completos_planilhas_2015_a_2025.csv`.

Este ficheiro final conterá **todos os dados** das planilhas de referência de 2015 a 2025, tal como pediu.
