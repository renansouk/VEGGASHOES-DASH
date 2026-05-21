from nicegui import ui
import pandas as pd
import plotly.express as px

df = pd.read_parquet('data/faturamento_processado.parquet')

@ui.page('/')
def main():
    ui.label('Dashboard de Vendas - Redeplast').classes('text-h3 text-bold')
    
     # ============================================
    # 4. KPIs
    # ============================================
    with ui.row().classes('w-full justify-between'):
        total_vendas = df['Valor de Faturamento'].sum()
        media_diaria = df.groupby('Data Emissao')['Valor de Faturamento'].sum().mean()
        total_pedidos = df['Numero Nota Fiscal'].nunique()
        
        with ui.card().classes('col-3'):
            ui.label('Total Faturado').classes('text-caption')
            ui.label(f'R$ {total_vendas:,.2f}').classes('text-h4 text-primary')
        
        with ui.card().classes('col-3'):
            ui.label('Média Diária').classes('text-caption')
            ui.label(f'R$ {media_diaria:,.2f}').classes('text-h4 text-secondary')
        
        with ui.card().classes('col-3'):
            ui.label('Notas Fiscais').classes('text-caption')
            ui.label(f'{total_pedidos:,}').classes('text-h4')
    
    # ============================================
    # 1. Faturamento por dia (agregado)
    # ============================================
    with ui.card().classes('w-full'):
        ui.label('Faturamento Diário').classes('text-h5')
        
        # Agrega por data
        daily = df.groupby('Data Emissao')['Valor de Faturamento'].sum().reset_index()
        
        fig1 = px.bar(
            daily, 
            x='Data Emissao', 
            y='Valor de Faturamento',
            title='Total por Dia',
            color_discrete_sequence=['#2E86AB']
        )
        ui.plotly(fig1).classes('w-full')
    
    # ============================================
    # 2. Faturamento por Marca
    # ============================================
    with ui.card().classes('w-full'):
        ui.label('Faturamento por Marca').classes('text-h5')
        
        brand = df.groupby('Marca')['Valor de Faturamento'].sum().reset_index()
        brand = brand.sort_values('Valor de Faturamento', ascending=False).head(10)
        
        fig2 = px.bar(
            brand,
            x='Marca',
            y='Valor de Faturamento',
            title='Top 10 Marcas',
            color='Valor de Faturamento',
            color_continuous_scale='Viridis'
        )
        ui.plotly(fig2).classes('w-full')
    
    # ============================================
    # 3. Faturamento por Canal
    # ============================================
    with ui.card().classes('w-full'):
        ui.label('Faturamento por Canal').classes('text-h5')
        
        canal = df.groupby('CANAL')['Valor de Faturamento'].sum().reset_index()
        
        fig3 = px.pie(
            canal,
            values='Valor de Faturamento',
            names='CANAL',
            title='Distribuição por Canal',
            hole=0.3
        )
        ui.plotly(fig3).classes('w-full')
    
   
    
    # ============================================
    # 5. Tabela de Dados (últimos 50 registros)
    # ============================================
    with ui.card().classes('w-full'):
        ui.label('Últimos Faturamentos').classes('text-h5')
        
        df_table = df.tail(50).copy()
        # Formata para exibição
        if 'Data Emissao' in df_table.columns:
            df_table['Data Emissao'] = df_table['Data Emissao'].dt.strftime('%d/%m/%Y')
        
        if 'Valor de Faturamento' in df_table.columns:
            df_table['Valor de Faturamento'] = df_table['Valor de Faturamento'].apply(lambda x: f'R$ {x:,.2f}')
        
        # Seleciona colunas relevantes
        cols = ['Data Emissao', 'Marca', 'CANAL', 'Destinatario', 'Valor de Faturamento']
        cols = [c for c in cols if c in df_table.columns]
        
        ui.table.from_pandas(df_table[cols]).classes('w-full')

ui.run(host='0.0.0.0', port=8080)
