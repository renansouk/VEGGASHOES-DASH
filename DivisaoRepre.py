import pandas as pd
import sqlite3


df = pd.read_excel(r'data\DIVISAO REPRESENTANTES POR CANAL.xlsx')


print(f'colunas = {df.columns}')  # colunas = df.columns)  # colunas = df.columns.toList()






colunas_index = [
    'CHAVE_COD_MARCA', 'CHAVE_CIDADE_UF', 'CODIGO', 'UF', 'LOCALIDADE',
    'MARCA', 'MESO', 'MICRO', 'CAPITAL', 'PORTE', 'LITORAL', 'POP', 'LAT',
    'LONG'
]

colunas_canais = [
    'INFANTIL', 'TRADICIONAL', 'MULTIMARCAS', 'MONOMARCA',
    'DIGITAL', 'EXPORTACAO', 'REPRESENTANTE', 'KEY', 'OUTROS',
    'CONSULTOR', 'PRIVAT LABEL'
]

divisao_linhas = df.melt(
    id_vars=colunas_index,
    value_vars=colunas_canais,
    var_name='CANAL',
    value_name='REPRE'
)

divisao_linhas = divisao_linhas[
    divisao_linhas['REPRE'].notna() &
    (divisao_linhas['REPRE'].astype(str).str.strip() != '')
]

divisao_linhas['CHAVE_IBGE_MARCA_CANAL'] = divisao_linhas.apply(
    lambda x: f"{x['CHAVE_COD_MARCA']}-{x['CANAL']}", axis=1
)
print(divisao_linhas.head())




divisao_linhas.to_csv('data\DivisaoRepre.csv', index=False)


