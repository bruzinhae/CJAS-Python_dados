# Rode no terminal:
# streamlit run testee.py 
#Teste com outra cor

import streamlit as st
import pandas as pd
import plotly.express as px

# --- Configuração da Página ---
st.set_page_config(
    page_title="Inscrições",
    layout="wide",
)

st.markdown("""
<style>

/* ---------- FUNDO GERAL ---------- */
.stApp {
    background: linear-gradient(180deg, #19485F, #163B4D);
    color: #D9E0A4;
    font-family: 'Segoe UI', sans-serif;
}

/* ---------- SIDEBAR ---------- */
section[data-testid="stSidebar"] {
    background-color: #163B4D;
}

/* ---------- MULTISELECT ---------- */

/* caixa */
div[data-baseweb="select"] > div {
    background-color: #19485F !important;
    color: #D9E0A4 !important;
    border: 1px solid #D9E0A4 !important;
}

/* tag selecionada */
span[data-baseweb="tag"] {
    background-color: #D9E0A4 !important;
    color: #19485F !important;
}

/* remove foco vermelho geral */
*:focus {
    outline: none !important;
    box-shadow: 0 0 0 2px #D9E0A4 !important;
}

/* ---------- SLIDER ---------- */

/* trilho */
.stSlider > div > div {
    color: #D9E0A4 !important;
}

/* bolinha */
.stSlider div[role="slider"] {
    background-color: #D9E0A4 !important;
    border: 2px solid #19485F !important;
}

/* ---------- BOTÕES ---------- */
div.stButton > button {
    background-color: #D9E0A4;
    color: #19485F;
    border-radius: 25px;
    border: none;
    font-weight: bold;
}

div.stButton > button:hover {
    background-color: #cdd88f;
}

/* ---------- CARDS ---------- */
.card {
    background: rgba(217, 224, 164, 0.08);
    backdrop-filter: blur(8px);
    padding: 25px;
    border-radius: 20px;
    border: 1px solid rgba(217,224,164,0.3);
    text-align: center;
    transition: 0.3s ease;
}

.card:hover {
    transform: translateY(-6px);
    box-shadow: 0 0 20px rgba(217,224,164,0.4);
}

.big-number {
    font-size: 36px;
    font-weight: bold;
    margin-bottom: 8px;
    color: #D9E0A4;
}

</style>
""", unsafe_allow_html=True)

# --- Carregamento dos dados ---
df = pd.read_csv("inscricoes_acampamento.csv")

df['id_de_membro'] = pd.to_numeric(df['id_de_membro'], errors='coerce')
df['membro'] = df['id_de_membro'].apply(
    lambda x: "Membro" if pd.notna(x) else "Não Membro"
)

# --- Sidebar ---
st.sidebar.header("🔍 Filtros")

sessoes_disponiveis = sorted(df['sessao'].unique())
sessoes_selecionadas = st.sidebar.multiselect(
    "Sessão",
    sessoes_disponiveis,
    default=sessoes_disponiveis
)

tipo_participante = st.sidebar.multiselect(
    "Tipo",
    df['membro'].unique(),
    default=df['membro'].unique()
)

idade_min = st.sidebar.slider(
    "Idade mínima",
    int(df['idade'].min()),
    int(df['idade'].max()),
    12
)

# --- Filtragem ---
df_filtrado = df[
    (df['sessao'].isin(sessoes_selecionadas)) &
    (df['membro'].isin(tipo_participante)) &
    (df['idade'] >= idade_min)
]

# --- Título ---
st.markdown("<h1 style='text-align:center;'> Inscrições</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; opacity:0.8;'>Análise geral dos participantes do acampamento</p>", unsafe_allow_html=True)

# --- Métricas ---
if not df_filtrado.empty:
    total_inscritos = df_filtrado.shape[0]
    media_idade = df_filtrado['idade'].mean()
    maior_idade = df_filtrado['idade'].max()
    nao_membros = df_filtrado[df_filtrado['membro'] == "Não Membro"].shape[0]
else:
    total_inscritos = media_idade = maior_idade = nao_membros = 0

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="card">
        <div class="big-number">{total_inscritos}</div>
        Total de Inscritos
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="card">
        <div class="big-number">{media_idade:.1f}</div>
        Idade Média
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="card">
        <div class="big-number">{maior_idade}</div>
        Maior Idade
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="card">
        <div class="big-number">{nao_membros}</div>
        Não Membros
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- Nova Paleta ---
cores = {
    "Membro": "#D9E0A4",
    "Não Membro": "#9fb3a8"
}

# --- Gráficos ---
col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    if not df_filtrado.empty:
        grafico_sessao = px.histogram(
            df_filtrado,
            x='sessao',
            color='membro',
            barmode='group',
            title="Distribuição por Sessão",
            color_discrete_map=cores
        )
        grafico_sessao.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#D9E0A4"
        )
        st.plotly_chart(grafico_sessao, use_container_width=True)

with col_graf2:
    if not df_filtrado.empty:
        grafico_idade = px.histogram(
            df_filtrado,
            x='idade',
            nbins=20,
            title="Distribuição de Idade",
            color_discrete_sequence=["#D9E0A4"]
        )
        grafico_idade.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#D9E0A4"
        )
        st.plotly_chart(grafico_idade, use_container_width=True)

# --- Pizza ---
if not df_filtrado.empty:
    contagem_membros = df_filtrado['membro'].value_counts().reset_index()
    contagem_membros.columns = ['tipo', 'quantidade']

    grafico_pizza = px.pie(
        contagem_membros,
        names='tipo',
        values='quantidade',
        hole=0.5,
        title="Proporção Membros vs Não Membros",
        color='tipo',
        color_discrete_map=cores
    )

    grafico_pizza.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#D9E0A4"
    )

    st.plotly_chart(grafico_pizza, use_container_width=True)

st.markdown("---")

# --- Tabela ---
st.subheader("📋 Lista de Inscritos")
st.dataframe(df_filtrado)