import pandas as pd
import streamlit as st
import requests 
from Functions.treating_datas import *
from Functions.get_reports_api import *
from datetime import timedelta, datetime
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# Configuração da página
st.set_page_config(
    page_title="Dashboard UNIDAS MEDICAL - YTD",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado premium (o mesmo do dashboard anterior)
st.markdown("""
<style>
    .main-header {
        font-size: 2.8rem;
        color: #1a5276;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: 800;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.1);
    }
    .main-sub-header {
        font-size: 2.2rem;
        color: #1a5276;
        border-bottom: 4px solid #3498db;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
        margin-bottom: 1.5rem;
        font-weight: 800;
        text-align: center;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .sub-header {
        font-size: 1.8rem;
        color: #2874a6;
        border-bottom: 3px solid #3498db;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
        margin-bottom: 1.5rem;
        font-weight: 700;
    }
    .kpi-card {
        background: linear-gradient(135deg, #1a5276 0%, #2874a6 100%);
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.15);
        height: 100%;
        color: white;
        text-align: center;
        transition: transform 0.3s ease;
    }
    .kpi-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 30px rgba(0, 0, 0, 0.2);
    }
    .kpi-icon {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }
    .kpi-value {
        font-size: 2rem;
        font-weight: 800;
        margin: 0.5rem 0;
    }
    .kpi-label {
        font-size: 1rem;
        opacity: 0.9;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .secondary-kpi {
        background: linear-gradient(135deg, #3498db 0%, #5dade2 100%);
        padding: 1.2rem;
        border-radius: 12px;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        height: 100%;
        color: white;
        text-align: center;
    }
    .secondary-kpi-value {
        font-size: 1.5rem;
        font-weight: 700;
        margin: 0.3rem 0;
    }
    .secondary-kpi-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    .progress-container {
        background: rgba(255, 255, 255, 0.2);
        border-radius: 10px;
        height: 10px;
        margin: 10px 0;
        overflow: hidden;
    }
    .progress-bar {
        height: 100%;
        background: white;
        border-radius: 10px;
    }
    .section-divider {
        height: 3px;
        background: linear-gradient(90deg, transparent 0%, #3498db 50%, transparent 100%);
        margin: 2rem 0;
        border: none;
    }
    .rep-card {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #3498db;
        margin-bottom: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }
    .rep-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    .refresh-button {
        background: linear-gradient(135deg, #1a5276 0%, #2874a6 100%);
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 5px;
        cursor: pointer;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .refresh-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
    }
    .ytd-positive {
        color: #27ae60;
        font-weight: bold;
    }
    .ytd-negative {
        color: #e74c3c;
        font-weight: bold;
    }
    .comparison-card {
        background: white;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 15px;
        border-left: 4px solid #3498db;
    }
</style>
""", unsafe_allow_html=True)

# Dados e configurações
lista_de_empresas = ["Brasil Med","Unidas BH","Unidas SP"]
meta_mensal = 2000000

meses_pt = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julio", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]

mes_atual = datetime.now().month
meses_decorridos = mes_atual - 1

# Pegando dados e cacheando
data_formatada = (datetime.now() - timedelta(hours=3)).strftime("%d/%m/%y")
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
    return df, dados_brutos

# Botão para atualizar dados (limpar cache)
col1, col2, col3 = st.columns([3, 2, 1])
with col3:
    if st.button("🔄 Atualizar Dados", help="Clique para buscar dados atualizados da API"):
        st.cache_data.clear()
        st.success("Cache limpo! Os dados serão atualizados na próxima execução.")
        st.rerun()

# Carrega os dados com cache
df, dados_brutos = dados()
df = df.loc[df['Mês_do_pedido'] != nome_mes]

vendas_mes_a_mes = df.groupby(['Mês_do_pedido','Mès_num']).agg({'Valor Faturado':'sum',
                                                      'Número da NF ':'nunique',}).reset_index()

vendas_mes_a_mes = vendas_mes_a_mes.rename(columns={'Número da NF ':'Pedidos'})
vendas_mes_a_mes = vendas_mes_a_mes.sort_values(by=['Mès_num'])

vendas_mes_a_mes['Ticket_médio'] = vendas_mes_a_mes['Valor Faturado']/vendas_mes_a_mes['Pedidos']

## Métricas Gerais: 
faturamento_do_ano = vendas_mes_a_mes['Valor Faturado'].sum()
meta_ano = meta_mensal * 12
meta_proporcional = (meta_mensal * meses_decorridos)

atingimento_meta_ano = faturamento_do_ano/meta_ano  * 100
atingimento_meta_proporcional = faturamento_do_ano/meta_proporcional * 100

ticket_medio_anual = vendas_mes_a_mes['Ticket_médio'].mean()

melhor_mes = vendas_mes_a_mes.sort_values(by=['Valor Faturado'],ascending=False)
melhor_mes = melhor_mes.head(1)
melhor_mes_nome = melhor_mes['Mês_do_pedido'].values[0]
melhor_mes_valor = melhor_mes['Valor Faturado'].values[0]

# Calcular crescimento mês a mês
vendas_mes_a_mes['Crescimento'] = vendas_mes_a_mes['Valor Faturado'].pct_change() * 100
vendas_mes_a_mes['Crescimento'] = vendas_mes_a_mes['Crescimento'].fillna(0)

# Calcular média móvel de 3 meses
vendas_mes_a_mes['Media_Movel'] = vendas_mes_a_mes['Valor Faturado'].rolling(window=3, min_periods=1).mean()

# HEADER PRINCIPAL
st.markdown('<p class="main-header">Dashboard de Vendas - UNIDAS MEDICAL YTD</p>', unsafe_allow_html=True)
st.markdown(f'<h3 style="text-align: center; color: #7f8c8d; margin-bottom: 2rem;">Análise de Performance Anual - {datetime.now().year}</h3>', unsafe_allow_html=True)

# KPIs PRINCIPAIS - DESIGN PREMIUM
st.markdown('<p class="main-sub-header">📈 VISÃO GERAL DO ANO</p>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="kpi-card">
        <div class="kpi-icon">🎯</div>
        <div class="kpi-value">R$ {meta_ano:,.0f}</div>
        <div class="kpi-label">Meta Anual</div>
    </div>
    """.format(meta_ano=meta_ano), unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="kpi-card">
        <div class="kpi-icon">💰</div>
        <div class="kpi-value">R$ {faturamento_do_ano:,.0f}</div>
        <div class="kpi-label">Faturamento YTD</div>
    </div>
    """.format(faturamento_do_ano=faturamento_do_ano), unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="kpi-card">
        <div class="kpi-icon">📊</div>
        <div class="kpi-value">{atingimento_meta_proporcional:,.1f}%</div>
        <div class="kpi-label">Atingimento Meta Proporcional</div>
        <div class="progress-container">
            <div class="progress-bar" style="width: {progresso_value}%;"></div>
        </div>
    </div>
    """.format(atingimento_meta_proporcional=atingimento_meta_proporcional, progresso_value=min(atingimento_meta_proporcional, 100)), unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="kpi-card">
        <div class="kpi-icon">🎫</div>
        <div class="kpi-value">R$ {ticket_medio_anual:,.0f}</div>
        <div class="kpi-label">Ticket Médio Anual</div>
    </div>
    """.format(ticket_medio_anual=ticket_medio_anual), unsafe_allow_html=True)

# DIVISÃO VISUAL
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# EVOLUÇÃO MENSAL
st.markdown('<p class="sub-header">📈 Evolução Mensal de Faturamento</p>', unsafe_allow_html=True)

# Gráfico de linhas para faturamento mensal
fig = make_subplots(specs=[[{"secondary_y": True}]])

# Adicionar faturamento mensal
fig.add_trace(
    go.Scatter(
        x=vendas_mes_a_mes['Mês_do_pedido'], 
        y=vendas_mes_a_mes['Valor Faturado'],
        mode='lines+markers+text',
        name='Faturamento',
        line=dict(color='#3498db', width=3),
        marker=dict(size=8),
        text=[f'R${x:,.0f}' for x in vendas_mes_a_mes['Valor Faturado']],
        textposition='top center',
        hovertemplate='<b>Mês:</b> %{x}<br><b>Faturamento:</b> R$ %{y:,.2f}<extra></extra>'
    ),
    secondary_y=False
)

# Adicionar média móvel
fig.add_trace(
    go.Scatter(
        x=vendas_mes_a_mes['Mês_do_pedido'], 
        y=vendas_mes_a_mes['Media_Movel'],
        mode='lines',
        name='Média Móvel (3 meses)',
        line=dict(color='#e74c3c', width=2, dash='dash'),
        hovertemplate='<b>Mês:</b> %{x}<br><b>Média Móvel:</b> R$ %{y:,.2f}<extra></extra>'
    ),
    secondary_y=False
)

# Adicionar meta mensal como linha
fig.add_hline(y=meta_mensal, line_dash="dot", line_color="green", annotation_text="Meta Mensal", 
              annotation_position="bottom right")

# Configurar layout
fig.update_layout(
    title='Evolução do Faturamento Mensal',
    xaxis_title='Mês',
    yaxis_title='Faturamento (R$)',
    plot_bgcolor='white',
    paper_bgcolor='white',
    height=500,
    showlegend=True,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

# Configurar eixos
fig.update_yaxes(title_text="Faturamento (R$)", secondary_y=False, tickprefix="R$ ")
fig.update_xaxes(tickangle=-45)

st.plotly_chart(fig, use_container_width=True)

# DIVISÃO VISUAL
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# ANÁLISE COMPARATIVA
st.markdown('<p class="sub-header">📊 Análise Comparativa Mensal</p>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    # Crescimento mês a mês
    st.markdown("##### 📈 Crescimento Mês a Mês")
    
    # Calcular estatísticas de crescimento
    crescimento_positivo = vendas_mes_a_mes[vendas_mes_a_mes['Crescimento'] > 0].shape[0]
    crescimento_negativo = vendas_mes_a_mes[vendas_mes_a_mes['Crescimento'] < 0].shape[0]
    crescimento_medio = vendas_mes_a_mes['Crescimento'].mean()
    
    # Exibir métricas de crescimento
    growth_col1, growth_col2, growth_col3 = st.columns(3)
    
    with growth_col1:
        st.markdown(f"""
        <div class="secondary-kpi">
            <div style="font-size: 1.8rem;">📈</div>
            <div class="secondary-kpi-value">{crescimento_positivo}</div>
            <div class="secondary-kpi-label">Meses com Crescimento</div>
        </div>
        """, unsafe_allow_html=True)
    
    with growth_col2:
        st.markdown(f"""
        <div class="secondary-kpi">
            <div style="font-size: 1.8rem;">📉</div>
            <div class="secondary-kpi-value">{crescimento_negativo}</div>
            <div class="secondary-kpi-label">Meses com Queda</div>
        </div>
        """, unsafe_allow_html=True)
    
    with growth_col3:
        st.markdown(f"""
        <div class="secondary-kpi">
            <div style="font-size: 1.8rem;">📊</div>
            <div class="secondary-kpi-value">{crescimento_medio:.1f}%</div>
            <div class="secondary-kpi-label">Crescimento Médio</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Gráfico de barras para crescimento
    fig_crescimento = go.Figure()
    
    # Cores baseadas no valor (verde para positivo, vermelho para negativo)
    colors = ['#27ae60' if x >= 0 else '#e74c3c' for x in vendas_mes_a_mes['Crescimento']]
    
    fig_crescimento.add_trace(go.Bar(
        x=vendas_mes_a_mes['Mês_do_pedido'],
        y=vendas_mes_a_mes['Crescimento'],
        marker_color=colors,
        hovertemplate='<b>Mês:</b> %{x}<br><b>Crescimento:</b> %{y:.2f}%<extra></extra>'
    ))
    
    fig_crescimento.update_layout(
        title='Crescimento Mensal (%)',
        xaxis_title='Mês',
        yaxis_title='Crescimento (%)',
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=400,
        showlegend=False
    )
    
    st.plotly_chart(fig_crescimento, use_container_width=True)

with col2:
    # Comparação com o melhor mês
    st.markdown("##### 🏆 Comparação com o Melhor Mês")
    st.markdown(f"**Melhor mês:** {melhor_mes_nome} - R$ {melhor_mes_valor:,.0f}")
    
    # Calcular diferença percentual em relação ao melhor mês
    vendas_mes_a_mes['Vs_Melhor_Mes'] = (vendas_mes_a_mes['Valor Faturado'] / melhor_mes_valor) * 100
    
    # Gráfico de comparação
    fig_comparacao = go.Figure()
    
    fig_comparacao.add_trace(go.Bar(
        x=vendas_mes_a_mes['Mês_do_pedido'],
        y=vendas_mes_a_mes['Vs_Melhor_Mes'],
        marker_color=['#f39c12' if x == melhor_mes_nome else '#3498db' for x in vendas_mes_a_mes['Mês_do_pedido']],
        hovertemplate='<b>Mês:</b> %{x}<br><b>% do Melhor Mês:</b> %{y:.1f}%<extra></extra>'
    ))
    
    # Adicionar linha de referência em 100%
    fig_comparacao.add_hline(y=100, line_dash="dash", line_color="green", annotation_text="Melhor Mês = 100%")
    
    fig_comparacao.update_layout(
        title='Desempenho em Relação ao Melhor Mês (%)',
        xaxis_title='Mês',
        yaxis_title='Percentual do Melhor Mês (%)',
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=400,
        showlegend=False
    )
    
    st.plotly_chart(fig_comparacao, use_container_width=True)
    
    # Estatísticas de comparação
    media_vs_melhor = vendas_mes_a_mes['Vs_Melhor_Mes'].mean()
    meses_acima_media = vendas_mes_a_mes[vendas_mes_a_mes['Vs_Melhor_Mes'] > media_vs_melhor].shape[0]
    
    st.metric("Média em Relação ao Melhor Mês", f"{media_vs_melhor:.1f}%")
    st.metric("Meses Acima da Média", f"{meses_acima_media} meses")

# DIVISÃO VISUAL
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# ANÁLISE DE TICKET MÉDIO
st.markdown('<p class="sub-header">🎫 Análise de Ticket Médio</p>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    # Evolução do ticket médio
    fig_ticket = go.Figure()
    
    fig_ticket.add_trace(go.Scatter(
        x=vendas_mes_a_mes['Mês_do_pedido'], 
        y=vendas_mes_a_mes['Ticket_médio'],
        mode='lines+markers',
        name='Ticket Médio',
        line=dict(color='#9b59b6', width=3),
        marker=dict(size=8),
        hovertemplate='<b>Mês:</b> %{x}<br><b>Ticket Médio:</b> R$ %{y:,.2f}<extra></extra>'
    ))
    
    fig_ticket.update_layout(
        title='Evolução do Ticket Médio',
        xaxis_title='Mês',
        yaxis_title='Ticket Médio (R$)',
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=400,
        showlegend=False
    )
    
    st.plotly_chart(fig_ticket, use_container_width=True)

with col2:
    # Relação entre ticket médio e faturamento
    fig_relacao = go.Figure()
    
    # Gráfico de bolhas com tamanho baseado no faturamento
    fig_relacao.add_trace(go.Scatter(
        x=vendas_mes_a_mes['Ticket_médio'],
        y=vendas_mes_a_mes['Valor Faturado'],
        mode='markers+text',
        marker=dict(
            size=vendas_mes_a_mes['Valor Faturado']/50000,
            color=vendas_mes_a_mes['Mès_num'],
            colorscale='Blues',
            showscale=True,
            colorbar=dict(title="Mês")
        ),
        text=vendas_mes_a_mes['Mês_do_pedido'],
        textposition='middle center',
        hovertemplate='<b>Mês:</b> %{text}<br><b>Ticket Médio:</b> R$ %{x:,.2f}<br><b>Faturamento:</b> R$ %{y:,.2f}<extra></extra>'
    ))
    
    fig_relacao.update_layout(
        title='Relação: Ticket Médio vs Faturamento',
        xaxis_title='Ticket Médio (R$)',
        yaxis_title='Faturamento (R$)',
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=400,
        showlegend=False
    )
    
    st.plotly_chart(fig_relacao, use_container_width=True)

# DIVISÃO VISUAL
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# RESUMO ESTATÍSTICO
st.markdown('<p class="sub-header">📋 Resumo Estatístico</p>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="comparison-card">
        <h4 style="margin-top: 0; color: #2c3e50;">📅 Melhor Mês</h4>
        <p style="font-size: 1.2rem; margin-bottom: 0;"><strong>{melhor_mes_nome}</strong></p>
        <p style="font-size: 1.5rem; color: #27ae60; margin: 0;"><strong>R$ {melhor_mes_valor:,.0f}</strong></p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    pior_mes = vendas_mes_a_mes.sort_values(by=['Valor Faturado']).head(1)
    pior_mes_nome = pior_mes['Mês_do_pedido'].values[0]
    pior_mes_valor = pior_mes['Valor Faturado'].values[0]
    
    st.markdown(f"""
    <div class="comparison-card">
        <h4 style="margin-top: 0; color: #2c3e50;">📅 Pior Mês</h4>
        <p style="font-size: 1.2rem; margin-bottom: 0;"><strong>{pior_mes_nome}</strong></p>
        <p style="font-size: 1.5rem; color: #e74c3c; margin: 0;"><strong>R$ {pior_mes_valor:,.0f}</strong></p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    media_mensal = vendas_mes_a_mes['Valor Faturado'].mean()
    st.markdown(f"""
    <div class="comparison-card">
        <h4 style="margin-top: 0; color: #2c3e50;">📊 Média Mensal</h4>
        <p style="font-size: 1.5rem; color: #3498db; margin: 0;"><strong>R$ {media_mensal:,.0f}</strong></p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    desvio_padrao = vendas_mes_a_mes['Valor Faturado'].std()
    coeficiente_variacao = (desvio_padrao / media_mensal) * 100
    
    st.markdown(f"""
    <div class="comparison-card">
        <h4 style="margin-top: 0; color: #2c3e50;">📈 Volatilidade</h4>
        <p style="font-size: 1.2rem; margin-bottom: 0;"><strong>Coeficiente de Variação</strong></p>
        <p style="font-size: 1.5rem; color: #9b59b6; margin: 0;"><strong>{coeficiente_variacao:.1f}%</strong></p>
    </div>
    """, unsafe_allow_html=True)
    # Adicionar insights automáticos
    if coeficiente_variacao > 30:
        insight = "📉 Alta volatilidade"
    elif coeficiente_variacao > 15:
        insight = "📊 Variabilidade moderada"
    else:
        insight = "📈 Estabilidade excelente"

    st.info(f"**Insight:** {insight}")

# Tabela detalhada
st.subheader("📋 Detalhamento Mensal")
vendas_mes_a_mes_display = vendas_mes_a_mes.copy()
vendas_mes_a_mes_display['Valor Faturado'] = vendas_mes_a_mes_display['Valor Faturado'].apply(lambda x: f'R$ {x:,.2f}')
vendas_mes_a_mes_display['Ticket_médio'] = vendas_mes_a_mes_display['Ticket_médio'].apply(lambda x: f'R$ {x:,.2f}')
vendas_mes_a_mes_display['Crescimento'] = vendas_mes_a_mes_display['Crescimento'].apply(lambda x: f'{x:.1f}%')
vendas_mes_a_mes_display['Vs_Melhor_Mes'] = vendas_mes_a_mes_display['Vs_Melhor_Mes'].apply(lambda x: f'{x:.1f}%')

# Aplicar formatação condicional para crescimento
def color_crescimento(val):
    if float(val.replace('%', '')) > 0:
        return 'color: #27ae60; font-weight: bold;'
    elif float(val.replace('%', '')) < 0:
        return 'color: #e74c3c; font-weight: bold;'
    else:
        return 'color: black;'

st.dataframe(
    vendas_mes_a_mes_display.style.map(color_crescimento, subset=['Crescimento']),
    use_container_width=True,
    hide_index=True
)

# FOOTER
st.markdown("---")
st.markdown("<p style='text-align: center; color: #7f8c8d;'>Dashboard YTD desenvolvido para UNIDAS MEDICAL | Atualizado em {}</p>".format((datetime.now() - timedelta(hours=3)).strftime("%d/%m/%Y %H:%M")), unsafe_allow_html=True)