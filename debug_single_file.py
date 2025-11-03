
import pandas as pd
try:
    df = pd.read_excel('planilhas/Copiaa_dea_04a_2016a_arta_33.xlsx', header=None)
    print(df.head(15).to_string())
except Exception as e:
    print(e)
