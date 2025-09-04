import pandas as pd
import streamlit as st
import requests 
from Functions.treating_datas import *
from Functions.get_reports_api import *
from datetime import timedelta, datetime
import numpy as np
import plotly.graph_objects as go

lista_de_empresas = ["Brasil Med","Unidas BH","Unidas SP"]

meta_mes = 2000000

meses_pt = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julio", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]

mes_atual = datetime.now().month
data_formatada = datetime.now().strftime("%d/%m/%y")
nome_mes = meses_pt[mes_atual - 1]

@st.cache_data(ttl=3600)
def cached_main():
    return main()

@st.cache_data
def cached_treating_data(dados_brutos):
    return treating_data_from_pipe(dados_brutos)

def dados():
    dados_brutos = cached_main()
    df = cached_treating_data(dados_brutos)
    return df,dados_brutos

# Carrega os dados com cache
df,dados_brutos = dados()
df['Empresa_tratada'] = df['CNPJ_empresa'].apply(encontrar_empresa)

df_mes = df.loc[df['Mês_do_pedido'] == nome_mes]
df_dia = df.loc[df['Data_do_pedido'] == data_formatada]

# Gráfico de vendas diárias
vendas_diarias = df_mes.groupby(['Data_do_pedido']).agg({'Valor Faturado':'sum'}).reset_index()
vendas_diarias = vendas_diarias.sort_values('Data_do_pedido')

# Criar gráfico com Plotly (versão compatível)
fig = go.Figure()

fig.add_trace(go.Bar(
    x=vendas_diarias['Data_do_pedido'],
    y=vendas_diarias['Valor Faturado'],
    marker_color=['#1f77b4', '#4c96cb', '#78b5e2', '#a5d4f5', '#d1ecff'],
    hovertemplate='<b>Data:</b> %{x}<br><b>Valor:</b> R$ %{y:,.2f}<extra></extra>'
))

# Personalizar layout
fig.update_layout(
    title=f'Vendas Diárias - {nome_mes}',
    xaxis_title='Data',
    yaxis_title='Valor Faturado (R$)',
    plot_bgcolor='white',
    paper_bgcolor='white',
    font=dict(size=12),
    height=400
)

# Melhor dia do mês
melhor_dia_gp = df_mes.groupby(['Data_do_pedido']).agg({'Valor Faturado':'sum'}).reset_index()
melhor_dia_gp = melhor_dia_gp.sort_values(by=['Valor Faturado'],ascending=False)
melhor_dia_gp = melhor_dia_gp.head(1)

faturamento_melhor_dia = melhor_dia_gp['Valor Faturado'].sum()
Faturamento_dia = df_dia['Valor Faturado'].sum()
Faturamento_mes = df_mes['Valor Faturado'].sum()
quantidade_vendida = df_mes['Número da NF '].nunique()
atingimento_meta_mes = Faturamento_mes/meta_mes * 100
ticket_medio_mes = Faturamento_mes/quantidade_vendida

# Layout do Streamlit
st.title(f"Dashboard De Vendas - UNIDAS MEDICAL")
st.header(f"Análise das Vendas Da Rede - {nome_mes}")

# Métricas em colunas
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(f"Meta mês de {nome_mes}", f"R$ {meta_mes:,.2f}")

with col2:
    st.metric("Faturamento Mês", f"R$ {Faturamento_mes:,.2f}")

with col3:
    st.metric("Atingimento de Meta", f"{atingimento_meta_mes:,.1f}%")

with col4:
   st.metric("Ticket Médio", f"R$ {ticket_medio_mes:,.2f}")

# Gráfico de vendas diárias
st.subheader("Vendas Diárias Detalhadas")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Data de Hoje", data_formatada)

with col2:
    st.metric("Faturamento Hoje", f"R$ {Faturamento_dia:,.2f}")

with col3:
    st.metric("Melhor Dia", f"R$ {faturamento_melhor_dia:,.2f}")
    
st.plotly_chart(fig, use_container_width=True)

# Tabela com dados detalhados
st.subheader("Detalhamento por Data")
st.dataframe(
    vendas_diarias.style.format({
        'Valor Faturado': 'R$ {:.2f}'
    }).background_gradient(subset=['Valor Faturado'], cmap='Blues'),
    use_container_width=True
)

st.subheader("🏆 Top 5 Produtos por Faturamento")

produtos_groupby = df_mes.groupby(["Produtos"]).agg({'Valor Faturado':'sum'}).reset_index()
produtos_groupby = produtos_groupby.sort_values(by=['Valor Faturado'],ascending=False)
produtos_groupby = produtos_groupby.head(5)

# Gráfico de barras horizontais
fig = go.Figure()

fig.add_trace(go.Bar(
    y=produtos_groupby['Produtos'],
    x=produtos_groupby['Valor Faturado'],
    orientation='h',
    marker_color=['#1f77b4', '#4c96cb', '#78b5e2', '#a5d4f5', '#d1ecff'],
    hovertemplate='<b>%{y}</b><br>Faturamento: R$ %{x:,.2f}<extra></extra>'
))

fig.update_layout(
    title='Top 5 Produtos - Ranking por Faturamento',
    xaxis_title='Faturamento (R$)',
    yaxis_title='Produtos',
    plot_bgcolor='white',
    paper_bgcolor='white',
    height=400,
    showlegend=False
)

st.plotly_chart(fig, use_container_width=True)

# Tabela estilizada
st.subheader("**Detalhamento dos Top 5:**")
st.dataframe(
    produtos_groupby.style.format({
        'Valor Faturado': 'R$ {:.2f}'
    }).highlight_max(subset=['Valor Faturado'], color='#d1ecff')
    .background_gradient(subset=['Valor Faturado'], cmap='Blues'),
    use_container_width=True,
    hide_index=True
)


st.header(f"Análise das vendas por CNPJ - {nome_mes}")
empresa_input = st.selectbox("Qual Empresa você deseja Analisar?",lista_de_empresas,
                             index=None)

st.dataframe(df)
st.dataframe(dados_brutos)


