# streamlit run dashboard.py

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ─── Página ───────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Inscrições · Acampamento",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
* { box-sizing: border-box; }

.stApp {
    background-color: #0F1117;
    color: #E8EAF0;
    font-family: 'Inter', 'Segoe UI', sans-serif;
}

section[data-testid="stSidebar"] {
    background-color: #16181F !important;
    border-right: 1px solid rgba(255,255,255,0.06);
    padding-top: 0 !important;
}
section[data-testid="stSidebar"] > div { padding-top: 0 !important; }

.brand-block {
    display: flex; align-items: center; gap: 10px;
    padding: 24px 20px 20px 20px;
    border-bottom: 1px solid rgba(255,255,255,0.07);
    margin-bottom: 16px;
}
.brand-icon {
    width: 32px; height: 32px;
    background: linear-gradient(135deg, #6C63FF, #9B59B6);
    border-radius: 8px; display: flex; align-items: center;
    justify-content: center; font-size: 16px; flex-shrink: 0;
}
.brand-name { font-size: 15px; font-weight: 700; color: #FFF; letter-spacing: .3px; }

.nav-section-label {
    font-size: 10px; font-weight: 600; letter-spacing: 1.2px;
    text-transform: uppercase; color: rgba(255,255,255,.3);
    padding: 8px 20px 4px 20px; margin-top: 4px;
}
.nav-item {
    display: flex; align-items: center; gap: 10px;
    padding: 9px 20px; border-radius: 8px; margin: 2px 12px;
    font-size: 13.5px; font-weight: 500; color: rgba(255,255,255,.55);
}
.nav-item.active { background: rgba(108,99,255,.15); color: #A89EFF; font-weight: 600; }
.nav-icon { font-size: 15px; width: 18px; text-align: center; }
.sidebar-divider { border: none; border-top: 1px solid rgba(255,255,255,.06); margin: 12px 20px; }

div[data-baseweb="select"] > div {
    background-color: #1E2028 !important; color: #E8EAF0 !important;
    border: 1px solid rgba(255,255,255,.1) !important; border-radius: 8px !important;
}
span[data-baseweb="tag"] {
    background-color: rgba(108,99,255,.25) !important;
    color: #A89EFF !important; border-radius: 4px !important;
}
*:focus { outline: none !important; box-shadow: 0 0 0 2px rgba(108,99,255,.4) !important; }
.stSlider div[role="slider"] { background-color: #6C63FF !important; border: 2px solid #0F1117 !important; }

.page-title { font-size: 22px; font-weight: 700; color: #FFF; letter-spacing: -.3px; }
.page-subtitle { font-size: 13px; color: rgba(255,255,255,.4); margin-top: 2px; }

.metric-card {
    background: #16181F; border: 1px solid rgba(255,255,255,.07);
    border-radius: 14px; padding: 20px 22px; position: relative; overflow: hidden;
}
.metric-accent { position: absolute; top:0; right:0; width:80px; height:80px; border-radius: 0 14px 0 80px; opacity:.06; }
.metric-card-icon { width:36px; height:36px; border-radius:9px; display:flex; align-items:center; justify-content:center; font-size:17px; margin-bottom:14px; }
.metric-card-label { font-size:11.5px; font-weight:600; letter-spacing:.7px; text-transform:uppercase; color:rgba(255,255,255,.38); margin-bottom:6px; }
.metric-card-value { font-size:30px; font-weight:700; color:#FFF; letter-spacing:-.5px; line-height:1; }
.metric-card-sub { font-size:11.5px; color:rgba(255,255,255,.3); margin-top:6px; }

.chart-card {
    background: #16181F; border: 1px solid rgba(255,255,255,.07);
    border-radius: 14px; padding: 20px 22px 8px 22px; margin-bottom: 16px;
}
.chart-title { font-size:14px; font-weight:600; color:rgba(255,255,255,.85); margin-bottom:2px; }
.chart-sub { font-size:11px; color:rgba(255,255,255,.3); margin-bottom:8px; }

hr { border-color: rgba(255,255,255,.06) !important; margin: 24px 0 !important; }
.section-label { font-size:11px; font-weight:600; letter-spacing:1px; text-transform:uppercase; color:rgba(255,255,255,.3); margin-bottom:12px; }
</style>
""", unsafe_allow_html=True)


# ─── Dados ────────────────────────────────────────────────────────────────────
@st.cache_data
def carregar_dados():
    return pd.read_csv("inscricoes_acampamento.csv")

df = carregar_dados()
df['id_de_membro'] = pd.to_numeric(df['id_de_membro'], errors='coerce')
df['membro'] = df['id_de_membro'].apply(lambda x: "Membro" if pd.notna(x) else "Não Membro")


# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="brand-block">
        <div class="brand-icon">⛺</div>
        <div class="brand-name">Acampamento</div>
    </div>
    <div class="nav-section-label">Menu</div>
    <div class="nav-item active"><span class="nav-icon">📊</span> Inscrições</div>
    <div class="nav-item"><span class="nav-icon">👥</span> Participantes</div>
    <div class="nav-item"><span class="nav-icon">🗓️</span> Sessões</div>
    <div class="nav-item"><span class="nav-icon">📋</span> Relatórios</div>
    <hr class="sidebar-divider">
    <div class="nav-section-label">Conta</div>
    <div class="nav-item"><span class="nav-icon">⚙️</span> Configurações</div>
    <div class="nav-item"><span class="nav-icon">🚪</span> Sair</div>
    <hr class="sidebar-divider">
    <div class="nav-section-label" style="margin-top:16px;">Filtros</div>
    """, unsafe_allow_html=True)

    sessoes_disponiveis  = sorted(df['sessao'].unique())
    sessoes_selecionadas = st.multiselect("Sessão", sessoes_disponiveis, default=sessoes_disponiveis)
    tipo_participante    = st.multiselect("Tipo", df['membro'].unique(), default=df['membro'].unique())
    idade_min            = st.slider("Idade mínima", int(df['idade'].min()), int(df['idade'].max()), 12)


# ─── Filtro ───────────────────────────────────────────────────────────────────
df_f = df[
    (df['sessao'].isin(sessoes_selecionadas)) &
    (df['membro'].isin(tipo_participante)) &
    (df['idade'] >= idade_min)
]

total       = df_f.shape[0]
media_idade = df_f['idade'].mean() if not df_f.empty else 0
maior_idade = int(df_f['idade'].max()) if not df_f.empty else 0
nao_membros = df_f[df_f['membro'] == "Não Membro"].shape[0]
membros     = df_f[df_f['membro'] == "Membro"].shape[0]
pct_membros = (membros / total * 100) if total > 0 else 0

# ─── Layout Plotly compartilhado ─────────────────────────────────────────────
CORES = {"Membro": "#6C63FF", "Não Membro": "#3D4455"}
LAYOUT = dict(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font_color="rgba(255,255,255,0.55)",
    font_size=12,
    margin=dict(t=10, b=10, l=10, r=10),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="rgba(255,255,255,0.06)", borderwidth=1),
)


# ─── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div style="display:flex; align-items:flex-start; justify-content:space-between; margin-bottom:20px;">
    <div>
        <div class="page-title">Inscrições</div>
        <div class="page-subtitle">Análise geral dos participantes do acampamento</div>
    </div>
    <div style="background:#1E2028; border:1px solid rgba(255,255,255,.08); border-radius:8px;
                padding:6px 12px; font-size:12px; color:rgba(255,255,255,.5);">
        📅 2026
    </div>
</div>
""", unsafe_allow_html=True)


# ─── Métricas ─────────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
cards = [
    (c1, "👤", "#6C63FF", "Total Inscritos",  str(total),           "participantes no filtro"),
    (c2, "🎂", "#F59E0B", "Idade Média",       f"{media_idade:.1f}", "anos"),
    (c3, "📈", "#10B981", "Maior Idade",        str(maior_idade),    "anos registrados"),
    (c4, "🆕", "#EF4444", "Não Membros",        str(nao_membros),    f"{100-pct_membros:.0f}% do total"),
]
for col, icon, color, label, value, sub in cards:
    with col:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-accent" style="background:{color};"></div>
            <div class="metric-card-icon" style="background:{color}22; color:{color};">{icon}</div>
            <div class="metric-card-label">{label}</div>
            <div class="metric-card-value">{value}</div>
            <div class="metric-card-sub">{sub}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<div style='margin-bottom:20px'></div>", unsafe_allow_html=True)


# ─── Gráficos linha 1 ─────────────────────────────────────────────────────────
col_g1, col_g2 = st.columns([3, 2])

with col_g1:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">Distribuição por Sessão</div>', unsafe_allow_html=True)
    st.markdown('<div class="chart-sub">Inscritos por sessão e tipo de participante</div>', unsafe_allow_html=True)
    if not df_f.empty:
        fig = px.histogram(df_f, x='sessao', color='membro', barmode='group',
                           color_discrete_map=CORES,
                           labels={'sessao': 'Sessão', 'membro': '', 'count': 'Qtd'})
        fig.update_traces(marker_line_width=0)
        fig.update_layout(**LAYOUT, height=260,
                          xaxis=dict(showgrid=False),
                          yaxis=dict(gridcolor="rgba(255,255,255,0.05)"))
        st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_g2:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">Membros vs Não Membros</div>', unsafe_allow_html=True)
    st.markdown('<div class="chart-sub">Proporção por tipo de participante</div>', unsafe_allow_html=True)
    if not df_f.empty:
        contagem = df_f['membro'].value_counts().reset_index()
        contagem.columns = ['tipo', 'quantidade']
        fig2 = px.pie(contagem, names='tipo', values='quantidade', hole=0.62,
                      color='tipo', color_discrete_map=CORES)
        fig2.update_traces(
            textinfo='percent', textfont_size=13,
            marker=dict(line=dict(color="#0F1117", width=2))
        )
        fig2.add_annotation(
            text=f"<b>{total}</b><br><span style='font-size:10px'>total</span>",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=18, color="#FFFFFF"), align="center",
        )
        layout_pizza = LAYOUT.copy()

        layout_pizza["legend"] = {
                **LAYOUT["legend"],
                "orientation": "h",
                "y": -0.1,
            }

        fig2.update_layout(
                **layout_pizza,
                height=260,
                showlegend=True,
            )
        

        st.plotly_chart(fig2, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ─── Gráfico linha 2: idades ──────────────────────────────────────────────────
st.markdown('<div class="chart-card">', unsafe_allow_html=True)
st.markdown('<div class="chart-title">Distribuição de Idades</div>', unsafe_allow_html=True)
st.markdown('<div class="chart-sub">Frequência de participantes por faixa etária</div>', unsafe_allow_html=True)
if not df_f.empty:
    fig3 = px.histogram(df_f, x='idade', nbins=20,
                        color_discrete_sequence=["#6C63FF"],
                        labels={'idade': 'Idade', 'count': 'Qtd'})
    fig3.update_traces(marker_line_width=0, opacity=0.85)
    fig3.update_layout(**LAYOUT, height=220,
                       xaxis=dict(showgrid=False, dtick=1),
                       yaxis=dict(gridcolor="rgba(255,255,255,0.05)"))
    st.plotly_chart(fig3, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)


# ─── Tabela ───────────────────────────────────────────────────────────────────
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown('<div class="section-label">Lista de Inscritos</div>', unsafe_allow_html=True)
st.dataframe(df_f, use_container_width=True, hide_index=True, height=320)
