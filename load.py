import pandas as pd
import requests
from pathlib import Path


# Cria pasta para os dados
Path("data").mkdir(exist_ok=True)

# ============================================
# 1. Busca os dados da API de Faturamento
# ============================================
print("Buscando dados da API de Faturamento...")

api_faturamento = 'https://portal.redeplastrs.com.br/portalredeplast/api/redeplast/api_lista_faturamento.php?token=8GzlsB0N868liF7fTAE4QgAeV1R9MeXUt84l1GhlnPQ&data_inicio=2026-05-01&data_fim=2027-01-01'

response = requests.get(api_faturamento)

if response.status_code == 200:
    data = response.json()
    records = data['data'] if 'data' in data else data
    df_faturamento = pd.DataFrame(records)
    print(f"✅ {len(df_faturamento)} registros de faturamento")
else:
    print(f"❌ Erro: {response.status_code}")
    exit()

# ============================================
# 2. Transformações iniciais (simulando Power Query)
# ============================================

# Converte colunas de data para datetime
df_faturamento['Data Emissao'] = pd.to_datetime(df_faturamento['Data Emissao'], errors='coerce')

df_faturamento['Data Movimento'] = pd.to_datetime(df_faturamento['Data Movimento'], errors='coerce')

# Cria coluna de Ano (como no seu DAX)
df_faturamento['Ano'] = df_faturamento['Data Emissao'].dt.year

# Cria coluna de Mês
df_faturamento['Mes'] = df_faturamento['Data Emissao'].dt.month

# Cria coluna de Estação (simulando a lógica do DAX)
def get_estacao(mes):
    if mes <= 3:
        return "Inverno"
    elif mes <= 6:
        return "Primavera"
    elif mes <= 9:
        return "Verão"
    else:
        return "Outono"

df_faturamento['Estacao'] = df_faturamento['Mes'].apply(get_estacao)

# Cria AnoPedido (lógica do DAX: Outono adiciona +1 ao ano)
def get_ano_pedido(row):
    if row['Estacao'] == "Outono":
        return row['Ano'] + 1
    return row['Ano']

df_faturamento['AnoPedido'] = df_faturamento.apply(get_ano_pedido, axis=1)

# Cria CHAVE_ANO_ESTACAO (como no seu modelo)
df_faturamento['CHAVE_ANO_ESTACAO'] = df_faturamento['Estacao'] + " " + df_faturamento['AnoPedido'].astype(str)

# ============================================
# 3. Lógica do CANAL (traduzindo aquele SWITCH gigante)
# ============================================

# Listas de clientes digitais (do seu SWITCH no DAX)
clientes_digitais = ["12979", "15974", "23544", "27683", "29604", "31013", 
                      "3473", "3836", "4246", "4247", "6340", "67418", "70474", "31720"]

def get_canal(row):
    marca = str(row.get('Marca', ''))
    cod_cliente = str(row.get('Cod. Destinatario', ''))
    uf = str(row.get('UF', ''))
    tipo_cliente = str(row.get('Tipo de Cliente', ''))
    representante = str(row.get('Representante', ''))
    
    # Exportação
    if uf == "ZZ":
        return "EXPORTACAO"
    
    # Marcas Private Label
    if marca not in ["COLCCI", "MORMAII", "SANTA LOLLA LICENCIADO", "LILICA RIPILICA - TIGOR T. TIG"]:
        return "PRIVAT LABEL"
    
    # Redeplast
    if "Redeplast" in representante:
        return "Outros"
    
    # Representante
    if tipo_cliente == "REPRESENTANTE":
        return "REPRESENTANTE"
    
    # Franquia
    if "FRANQUIA" in tipo_cliente:
        return "MONOMARCA"
    
    # Digital
    if cod_cliente in clientes_digitais:
        return "DIGITAL"
    
    # Franquia/Monomarcas
    if tipo_cliente == "FRANQUIA/MONOMARCAS":
        return "MONOMARCA"
    
    # Lógica Infantil vs Tradicional (baseado em vendas da marca Lilica)
    # Nota: Isso exigiria uma agregação por cliente, que é mais complexa
    # Por enquanto, vamos simplificar
    if marca == "LILICA RIPILICA - TIGOR T. TIG":
        return "INFANTIL"
    
    return "TRADICIONAL"

df_faturamento['CANAL'] = df_faturamento.apply(get_canal, axis=1)

# ============================================
# 4. Salva os dados processados
# ============================================

# Salva em Parquet (precisa do pyarrow)
df_faturamento.to_parquet('data/faturamento_processado.parquet', index=False)

# Também salva uma versão CSV para debug
df_faturamento.to_csv('data/faturamento_processado.csv', index=False)

print(f"\n✅ Dados salvos!")
print(f"   - Parquet: data/faturamento_processado.parquet")
print(f"   - CSV: data/faturamento_processado.csv")
print(f"\n📊 Estatísticas:")
print(f"   - Total de registros: {len(df_faturamento)}")
print(f"   - Canais únicos: {df_faturamento['CANAL'].unique().tolist()}")
print(f"   - Marcas únicas: {df_faturamento['Marca'].nunique()}")
print(f"   - Período: {df_faturamento['Data Emissao'].min()} a {df_faturamento['Data Emissao'].max()}")