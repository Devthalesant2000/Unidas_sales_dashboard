import pandas as pd
import streamlit as st
import requests 
from Functions.treating_datas import *
from Functions.get_reports_api import *
from datetime import timedelta, datetime
import numpy as np
import plotly.graph_objects as go

# CSS personalizado premium
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
</style>
""", unsafe_allow_html=True)
# Dados e configurações
lista_de_empresas = ["Brasil Med","Unidas BH","Unidas SP"]
meta_mes = st.secrets['authentication']['meta_mes']

meses_pt = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julio", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]

mes_atual = datetime.now().month
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

df_mes = df.loc[df['Mês_do_pedido'] == nome_mes]
df_dia = df.loc[df['Data_do_pedido'] == data_formatada]

# Cálculos principais
vendas_diarias = df_mes.groupby(['Data_do_pedido']).agg({'Valor Faturado':'sum'}).reset_index()
vendas_diarias = vendas_diarias.sort_values('Data_do_pedido')

melhor_dia_gp = df_mes.groupby(['Data_do_pedido']).agg({'Valor Faturado':'sum'}).reset_index()
melhor_dia_gp = melhor_dia_gp.sort_values(by=['Valor Faturado'],ascending=False)
melhor_dia_gp = melhor_dia_gp.head(1)

faturamento_melhor_dia = melhor_dia_gp['Valor Faturado'].sum()
Faturamento_dia = df_dia['Valor Faturado'].sum()
Faturamento_mes = df_mes['Valor Faturado'].sum()
quantidade_vendida = df_mes['Número da NF '].nunique()
atingimento_meta_mes = Faturamento_mes/meta_mes * 100
ticket_medio_mes = Faturamento_mes/quantidade_vendida

# Calcular o valor do progresso (não pode ultrapassar 100%)
progresso_value = min(atingimento_meta_mes, 100)

# Função para formatar valores monetários com separador de milhar por ponto
def format_currency(value):
    return f"{value:,.0f}".replace(",", ".")
# Função para formatar valores com ponto como separador de milhar (para floats)
def format_currency_float(value):
    if pd.isna(value):
        return value
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


# HEADER PRINCIPAL
st.markdown('<p class="main-header">Dashboard de Vendas - UNIDAS MEDICAL</p>', unsafe_allow_html=True)
st.markdown(f'<h3 style="text-align: center; color: #7f8c8d; margin-bottom: 2rem;">Análise das Vendas da Rede - {nome_mes}</h3>', unsafe_allow_html=True)

# KPIs PRINCIPAIS - DESIGN PREMIUM
st.markdown('<p class="main-sub-header">📈 VISÃO GERAL DO MÊS</p>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-icon">🎯</div>
        <div class="kpi-value">R$ {format_currency(meta_mes)}</div>
        <div class="kpi-label">Meta do Mês</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-icon">💰</div>
        <div class="kpi-value">R$ {format_currency(Faturamento_mes)}</div>
        <div class="kpi-label">Faturamento Realizado</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-icon">📊</div>
        <div class="kpi-value">{atingimento_meta_mes:,.1f}%</div>
        <div class="kpi-label">Atingimento da Meta</div>
        <div class="progress-container">
            <div class="progress-bar" style="width: {progresso_value}%;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-icon">🎫</div>
        <div class="kpi-value">R$ {format_currency(ticket_medio_mes)}</div>
        <div class="kpi-label">Ticket Médio</div>
    </div>
    """, unsafe_allow_html=True)

# DIVISÃO VISUAL
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# VENDAS DIÁRIAS - DESIGN PREMIUM
st.markdown('<p class="sub-header">📅 Vendas Diárias Detalhadas</p>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div class="secondary-kpi">
        <div style="font-size: 1.8rem;">📅</div>
        <div class="secondary-kpi-value">{data_formatada}</div>
        <div class="secondary-kpi-label">Data de Hoje</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="secondary-kpi">
        <div style="font-size: 1.8rem;">💸</div>
        <div class="secondary-kpi-value">R$ {format_currency(Faturamento_dia)}</div>
        <div class="secondary-kpi-label">Faturamento Hoje</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="secondary-kpi">
        <div style="font-size: 1.8rem;">🚀</div>
        <div class="secondary-kpi-value">R$ {format_currency(faturamento_melhor_dia)}</div>
        <div class="secondary-kpi-label">Melhor Dia do Mês</div>
    </div>
    """, unsafe_allow_html=True)

# Gráfico de vendas diárias
fig_vendas = go.Figure()
fig_vendas.add_trace(go.Bar(
    x=vendas_diarias['Data_do_pedido'],
    y=vendas_diarias['Valor Faturado'],
    marker_color='#3498db',
    hovertemplate='<b>Data:</b> %{x}<br><b>Valor:</b> R$ %{y:,.2f}<extra></extra>'
))

fig_vendas.update_layout(
    title=f'Vendas Diárias - {nome_mes}',
    xaxis_title='Data',
    yaxis_title='Valor Faturado (R$)',
    plot_bgcolor='white',
    paper_bgcolor='white',
    font=dict(size=12),
    height=400
)

st.plotly_chart(fig_vendas, use_container_width=True)

# Tabela com dados detalhados
st.subheader("Detalhamento por Data")
st.dataframe(
    vendas_diarias.style.format({
        'Valor Faturado': format_currency_float
    }).background_gradient(subset=['Valor Faturado'], cmap='Blues'),
    use_container_width=True
)

# DIVISÃO VISUAL
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# TOP 5 PRODUTOS
st.markdown('<p class="sub-header">🏆 Top 5 Produtos por Faturamento</p>', unsafe_allow_html=True)

produtos_groupby = df_mes.groupby(["Produtos"]).agg({'Valor Faturado':'sum'}).reset_index()
produtos_groupby = produtos_groupby.sort_values(by=['Valor Faturado'],ascending=False)
produtos_groupby = produtos_groupby.head(5)

# Gráfico de barras horizontais
fig_produtos = go.Figure()
fig_produtos.add_trace(go.Bar(
    y=produtos_groupby['Produtos'],
    x=produtos_groupby['Valor Faturado'],
    orientation='h',
    marker_color=['#1a5276', '#2874a6', '#3498db', '#5dade2', '#85c1e9'],
    hovertemplate='<b>%{y}</b><br>Faturamento: R$ %{x:,.2f}<extra></extra>'
))

fig_produtos.update_layout(
    title='Top 5 Produtos - Ranking por Faturamento',
    xaxis_title='Faturamento (R$)',
    yaxis_title='Produtos',
    plot_bgcolor='white',
    paper_bgcolor='white',
    height=400,
    showlegend=False
)

st.plotly_chart(fig_produtos, use_container_width=True)

# Tabela estilizada
st.subheader("**Detalhamento dos Top 5:**")
st.dataframe(
    produtos_groupby.style.format({
        'Valor Faturado': format_currency_float
    }).highlight_max(subset=['Valor Faturado'], color='#d1ecff')
    .background_gradient(subset=['Valor Faturado'], cmap='Blues'),
    use_container_width=True,
    hide_index=True
)
# DIVISÃO VISUAL
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# PERFORMANCE DOS REPRESENTANTES
st.markdown('<p class="sub-header">👥 Performance Individual dos Representantes</p>', unsafe_allow_html=True)

representantes_gp = df_mes.groupby(['Representante']).agg({
    'Número da NF ': 'nunique',
    'Valor Faturado': 'sum'
}).reset_index()
representantes_gp = representantes_gp.rename(columns={'Número da NF ': 'Pedidos'})

# Dicionário de metas
vendedores_meta = {
    "Felipe Curi": 300000.00,
    "Noemia Sattin": 300000.00,
    "Distribuidores": 600000.00,
    "Ricardo santos": 300000.00,
    "Michele Rosete": 100000.00,
    "Juliana Kluge": 150000.00,
    "MELINA BASSO": 250000.00
}

# Adicionar meta e cálculo de atingimento
representantes_gp['Meta'] = representantes_gp['Representante'].map(vendedores_meta)
representantes_gp['Atingimento'] = (representantes_gp['Valor Faturado'] / representantes_gp['Meta']) * 100
representantes_gp['Atingimento'] = representantes_gp['Atingimento'].round(1)

# Calcular eficiência
media_ticket = representantes_gp['Valor Faturado'].sum() / representantes_gp['Pedidos'].sum()
representantes_gp['Eficiencia'] = ((representantes_gp['Valor Faturado'] / representantes_gp['Pedidos']) / media_ticket) * 100
representantes_gp['Eficiencia'] = representantes_gp['Eficiencia'].round(1)

# Cards dos representantes
for i in range(0, len(representantes_gp), 3):
    cols = st.columns(3)
    for j, col in enumerate(cols):
        if i + j < len(representantes_gp):
            rep = representantes_gp.iloc[i + j]
            
            # Definir cor baseada no atingimento (tons de azul)
            if rep['Atingimento'] >= 100:
                border_color = '#1a5276'  # Azul escuro - excelente
                status_text = "🎯 Meta Superada"
            elif rep['Atingimento'] >= 80:
                border_color = '#2874a6'  # Azul médio - bom
                status_text = "📈 Quase na Meta"
            elif rep['Atingimento'] >= 60:
                border_color = '#3498db'  # Azul - regular
                status_text = "↗️ Em Andamento"
            else:
                border_color = '#85c1e9'  # Azul claro - abaixo
                status_text = "⏱️ Início de Mês"
            
            # Mensagem contextual baseada na eficiência
            if rep['Eficiencia'] > 120:
                desempenho_text = "⭐ Alta Eficiência"
            elif rep['Eficiencia'] > 90:
                desempenho_text = "📊 Eficiência OK"
            else:
                desempenho_text = "🔍 Otimizar Ticket"
            
            with col:
                st.markdown(f"""
                <div class="rep-card" style="border-left-color: {border_color}">
                    <h4 style="margin:0; color: #2c3e50;">{rep['Representante']}</h4>
                    <p style="margin:5px 0;"><strong>Faturamento:</strong> R$ {format_currency(rep['Valor Faturado'])}</p>
                    <p style="margin:5px 0;"><strong>Meta:</strong> R$ {format_currency(rep['Meta'])}</p>
                    <p style="margin:5px 0;"><strong>Atingimento:</strong> <span style="color: {border_color}; font-weight: bold;">{rep['Atingimento']}%</span></p>
                    <p style="margin:5px 0; color: {border_color}; font-size: 12px;">{status_text}</p>
                    <p style="margin:5px 0;"><strong>Pedidos:</strong> {rep['Pedidos']}</p>
                    <p style="margin:5px 0;"><strong>Ticket Médio:</strong> R$ {format_currency(rep['Valor Faturado']/rep['Pedidos'])}</p>
                    <p style="margin:5px 0; font-size: 12px; color: #7f8c8d;">{desempenho_text}</p>
                </div>
                """, unsafe_allow_html=True)

# DIVISÃO VISUAL
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# GRÁFICO DE PERFORMANCE
st.markdown('<p class="sub-header">📊 Análise de Performance: Faturamento vs Pedidos</p>', unsafe_allow_html=True)

fig_perf = go.Figure()
fig_perf.add_trace(go.Scatter(
    x=representantes_gp['Pedidos'],
    y=representantes_gp['Valor Faturado'],
    mode='markers+text',
    marker=dict(
        size=representantes_gp['Valor Faturado']/1000,
        color=representantes_gp['Atingimento'],
        colorscale=[(0, '#d6eaf8'), (0.3, '#85c1e9'), (0.6, '#3498db'), (0.8, '#2874a6'), (1, '#1a5276')],
        showscale=True,
        cmin=0,
        cmax=120
    ),
    text=representantes_gp['Representante'],
    textposition='top center',
    hovertemplate='<b>%{text}</b><br>Pedidos: %{x}<br>Faturamento: R$ %{y:,.0f}<br>Meta: R$ %{meta:,.0f}<br>Atingimento: %{color:.1f}%<extra></extra>',
    meta=representantes_gp['Meta']
))

# Adicionar linha de referência para o FATURAMENTO MÉDIO
faturamento_medio = representantes_gp['Valor Faturado'].mean()
fig_perf.add_hline(y=faturamento_medio, line_dash="dash", line_color="#e74c3c")

# Adicionar linha da meta média
meta_media = representantes_gp['Meta'].mean()
fig_perf.add_hline(y=meta_media, line_dash="dot", line_color="#7f8c8d")

# Layout compatível
fig_perf['layout'].update(
    title='Relação: Quantidade de Pedidos vs Valor Faturado',
    xaxis=dict(title='Número de Pedidos'),
    yaxis=dict(title='Faturamento (R$)', tickprefix='R$ ', tickformat=',.0f'),
    plot_bgcolor='white',
    paper_bgcolor='white',
    height=500,
    hovermode='closest',
    showlegend=False
)

# Adicionar anotações manualmente
fig_perf['layout']['annotations'] = [
    dict(
        x=1, y=faturamento_medio,
        xref='paper', yref='y',
        text=f"Faturamento Médio: R$ {format_currency(faturamento_medio)}",
        showarrow=False,
        xanchor='right',
        yanchor='bottom',
        font=dict(color="#e74c3c")
    ),
    dict(
        x=1, y=meta_media,
        xref='paper', yref='y',
        text=f"Meta Média: R$ {format_currency(meta_media)}",
        showarrow=False,
        xanchor='right',
        yanchor='top',
        font=dict(color="#7f8c8d")
    )
]

st.plotly_chart(fig_perf, use_container_width=True)

# Legenda explicativa
st.info("""
**Como interpretar o gráfico de performance:** 
- 💰 **Bolhas maiores** = Maior faturamento
- 🎯 **Cores mais escuras** = Maior percentual de atingimento da meta
- 📈 **Acima da linha vermelha** = Acima da média de faturamento
- ⚫ **Linha cinza** = Meta média dos representantes
""")

# FOOTER
st.markdown("---")
st.markdown("<p style='text-align: center; color: #7f8c8d;'>Dashboard desenvolvido para UNIDAS MEDICAL | Atualizado em {}</p>".format((datetime.now() - timedelta(hours=3)).strftime("%d/%m/%Y %H:%M")), unsafe_allow_html=True)