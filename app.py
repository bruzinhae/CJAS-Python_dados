# streamlit run dashboard.py

import os
import glob
import datetime
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# ─── Página ───────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Inscrições · Acampamento",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Recarrega a página inteira a cada 60s — combinado com o cache por mtime
# abaixo, isso garante que o dashboard "perceba" sozinho quando você troca
# o arquivo CSV, sem precisar apertar F5.
st_autorefresh(interval=60_000, key="refresh_dashboard")

# ─── Paleta de cores (baseada em #43261D) ─────────────────────────────────────
BRAND        = "#43261D"
BRAND_LIGHT  = "#8B5A3C"
ACCENT_GOLD  = "#D4A373"
ACCENT_SAGE  = "#7C8B5C"
ACCENT_RUST  = "#B8553A"
TAUPE        = "#C9B8A3"   # tom neutro/secundário (substitui o "cinza" do template original)

BG_APP       = "#F3EAE0"
BG_SIDEBAR   = "#FFFFFF"
BG_CARD      = "#FFFFFF"
BORDER       = "rgba(67,38,29,0.10)"
TEXT_PRIMARY = "#2B1810"
TEXT_RGB     = "43,24,16"


# ─── Helpers de donut/ring em CSS puro (sem Plotly, pra encaixar exatamente
# dentro do card como no print de referência) ──────────────────────────────────
def conic_gradient(segments):
    """segments: lista de (pct, cor). Gera a string do conic-gradient CSS."""
    stops, acc = [], 0.0
    for p, color in segments:
        start = acc
        acc += p
        stops.append(f"{color} {start:.2f}% {acc:.2f}%")
    return "conic-gradient(" + ", ".join(stops) + ")"


def donut_card_html(label, value, sub, legend_items, donut_segments, grande=False):
    legend_html = "".join(
        f'<div class="legend-row"><span class="legend-dot" style="background:{color}"></span>'
        f'{name} <b>{pct:.0f}%</b></div>'
        for name, pct, color in legend_items
    )
    gradient = conic_gradient(donut_segments)
    classe_extra = " donut-card-lg" if grande else ""
    return f"""
    <div class="metric-card donut-card{classe_extra}">
        <div class="metric-card-label">{label}</div>
        <div class="metric-card-value">{value}</div>
        <div class="metric-card-sub">{sub}</div>
        <div class="donut-wrap">
            <div class="legend-col">{legend_html}</div>
            <div class="donut-circle" style="background:{gradient};">
                <div class="donut-hole"></div>
            </div>
        </div>
    </div>
    """


def ring_card_html(icon, label, value, sub, pct, color, grande=False):
    gradient = conic_gradient([(pct, color), (100 - pct, f"rgba({TEXT_RGB},.08)")])
    classe_extra = " ring-card-lg" if grande else ""
    return f"""
    <div class="metric-card ring-card{classe_extra}">
        <div class="ring-card-top">
            <div class="icon-outline">{icon}</div>
            <div class="ring-badge" style="background:{gradient};">
                <div class="ring-badge-hole" style="color:{color};">+{pct:.0f}%</div>
            </div>
        </div>
        <div class="metric-card-label" style="margin-top:14px;">{label}</div>
        <div class="metric-card-value">{value}</div>
        <div class="metric-card-sub">{sub}</div>
    </div>
    """


def stack_card_html(icon, label, value, sub, sub_color, grande=False):
    classe_extra = " stack-card-lg" if grande else ""
    return f"""
    <div class="metric-card stack-card{classe_extra}">
        <div class="stack-card-top">
            <div class="metric-card-label">{label}</div>
            <div class="icon-outline">{icon}</div>
        </div>
        <div class="metric-card-value">{value}</div>
        <div class="metric-card-sub" style="color:{sub_color};">{sub}</div>
    </div>

    """


# ─── CSS ──────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
* {{ box-sizing: border-box; }}

.stApp {{
    background-color: {BG_APP};
    color: {TEXT_PRIMARY};
    font-family: 'Inter', 'Segoe UI', sans-serif;
}}

section[data-testid="stSidebar"] {{
    background-color: {BG_SIDEBAR} !important;
    border-right: 1px solid {BORDER};
    padding-top: 0 !important;
}}
section[data-testid="stSidebar"] > div {{ padding-top: 0 !important; }}

.brand-block {{
    display: flex; align-items: center; gap: 10px;
    padding: 24px 20px 20px 20px;
    border-bottom: 1px solid {BORDER};
    margin-bottom: 16px;
}}
.brand-icon {{
    width: 32px; height: 32px;
    background: linear-gradient(135deg, {BRAND}, {BRAND_LIGHT});
    border-radius: 8px; display: flex; align-items: center;
    justify-content: center; font-size: 16px; flex-shrink: 0;
}}
.brand-name {{ font-size: 15px; font-weight: 700; color: {TEXT_PRIMARY}; letter-spacing: .3px; }}

.nav-section-label {{
    font-size: 10px; font-weight: 600; letter-spacing: 1.2px;
    text-transform: uppercase; color: rgba({TEXT_RGB},.4);
    padding: 8px 20px 4px 20px; margin-top: 4px;
}}
.nav-item {{
    display: flex; align-items: center; gap: 10px;
    padding: 9px 20px; border-radius: 8px; margin: 2px 12px;
    font-size: 13.5px; font-weight: 500; color: rgba({TEXT_RGB},.6);
}}
.nav-item.active {{ background: rgba(139,90,60,.16); color: {BRAND}; font-weight: 600; }}
.nav-icon {{ font-size: 15px; width: 18px; text-align: center; }}
.sidebar-divider {{ border: none; border-top: 1px solid {BORDER}; margin: 12px 20px; }}

/* Espaçamento entre os blocos de filtro (Sessão / Estaca / Unidade / Tipo / Idade) */
.filter-block-divider {{
    height: 1px;
    background: {BORDER};
    margin: 18px 4px 16px 4px;
}}

.support-card {{
    background: linear-gradient(160deg, rgba(139,90,60,.10), rgba(212,163,115,.20));
    border: 1px solid {BORDER}; border-radius: 14px;
    padding: 16px; margin: 14px 12px;
}}
.support-icon {{ font-size: 26px; }}
.support-title {{ font-weight: 700; font-size: 12.5px; color: {TEXT_PRIMARY}; margin-top: 8px; }}
.support-text {{ font-size: 11px; color: rgba({TEXT_RGB},.55); margin: 4px 0 12px 0; line-height: 1.4; }}
.support-btn {{
    display: inline-block; background: {BRAND}; color: #FFF;
    font-size: 11px; font-weight: 600; padding: 7px 16px; border-radius: 8px;
}}

div[data-baseweb="select"] > div {{
    background-color: {BG_CARD} !important; color: {TEXT_PRIMARY} !important;
    border: 1px solid {BORDER} !important; border-radius: 8px !important;
}}
span[data-baseweb="tag"] {{
    background-color: rgba(139,90,60,.16) !important;
    color: {BRAND} !important; border-radius: 4px !important;
}}
*:focus {{ outline: none !important; box-shadow: 0 0 0 2px rgba(139,90,60,.45) !important; }}
.stSlider div[role="slider"] {{ background-color: {BRAND_LIGHT} !important; border: 2px solid {BG_APP} !important; }}

/* st.pills (caixinhas de seleção) — combinando com a paleta da marca */
div[data-testid="stPills"] button {{
    border-radius: 999px !important;
    border: 1px solid {BORDER} !important;
    font-size: 12px !important;
}}
div[data-testid="stPills"] button[kind="pillsActive"],
div[data-testid="stPills"] button[aria-pressed="true"] {{
    background-color: {BRAND_LIGHT} !important;
    color: #FFF !important;
    border-color: {BRAND_LIGHT} !important;
}}

/* Botões de navegação (Inscrições/Participantes) — imitando o visual
   dos antigos .nav-item, mas agora são botões reais e funcionais */
section[data-testid="stSidebar"] div[data-testid="stButton"] button {{
    justify-content: flex-start !important;
    text-align: left !important;
    font-size: 13.5px !important;
}}
section[data-testid="stSidebar"] button[kind="secondary"] {{
    border: 1px solid {BORDER} !important;
    color: {BRAND} !important;
    border-radius: 8px !important;
    font-size: 12px !important;
    background-color: {BG_CARD} !important;
}}
section[data-testid="stSidebar"] button[kind="secondary"]:hover {{
    border-color: {BRAND_LIGHT} !important;
    color: {BRAND_LIGHT} !important;
}}
section[data-testid="stSidebar"] button[kind="primary"] {{
    background-color: rgba(139,90,60,.16) !important;
    color: {BRAND} !important;
    border: none !important;
    font-weight: 600 !important;
    box-shadow: none !important;
}}
section[data-testid="stSidebar"] button[kind="primary"]:hover {{
    background-color: rgba(139,90,60,.24) !important;
    color: {BRAND} !important;
}}

.page-title {{ font-size: 22px; font-weight: 700; color: {TEXT_PRIMARY}; letter-spacing: -.3px; }}
.page-subtitle {{ font-size: 13px; color: rgba({TEXT_RGB},.5); margin-top: 2px; }}

.header-right {{ display: flex; align-items: center; gap: 12px; }}
.date-pill {{
    background: {BG_CARD}; border: 1px solid {BORDER}; border-radius: 8px;
    padding: 7px 14px; font-size: 12px; color: rgba({TEXT_RGB},.6); white-space: nowrap;
}}
.theme-toggle {{
    background: {BG_CARD}; border: 1px solid {BORDER}; border-radius: 999px;
    padding: 6px 12px; font-size: 12px; color: rgba({TEXT_RGB},.5);
}}
.avatar-group {{ display: flex; align-items: center; gap: 8px; }}
.avatar-circle {{
    width: 30px; height: 30px; border-radius: 50%; background: {BRAND_LIGHT};
    color: #FFF; font-size: 11px; font-weight: 700;
    display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}}
.avatar-name {{ font-size: 12.5px; font-weight: 600; color: rgba({TEXT_RGB},.7); }}

.metric-card {{
    background: {BG_CARD}; border: 1px solid {BORDER};
    border-radius: 14px; padding: 18px 20px; height: 100%;
}}
.icon-outline {{
    width: 30px; height: 30px; border: 1px solid {BORDER}; border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 13px; color: rgba({TEXT_RGB},.55); flex-shrink: 0;
}}
.metric-card-label {{ font-size: 11.5px; font-weight: 600; letter-spacing: .5px; color: rgba({TEXT_RGB},.5); }}
.metric-card-value {{ font-size: 27px; font-weight: 700; color: {TEXT_PRIMARY}; letter-spacing: -.5px; line-height: 1.25; margin-top: 6px; }}
.metric-card-sub {{ font-size: 11.5px; color: rgba({TEXT_RGB},.4); margin-top: 4px; }}

.stack-card {{ margin-bottom: 14px; padding: 16px 18px; }}
.stack-card-top {{ display: flex; align-items: flex-start; justify-content: space-between; }}
.stack-card .metric-card-value {{ font-size: 25px; }}

/* Versão "grande" do stack-card: usada quando ele ocupa a coluna inteira
   sozinho (sem outro card empilhado embaixo), em vez de compartilhar
   espaço com 2 cards na mesma coluna. */
.stack-card-lg {{ margin-bottom: 0; padding: 22px 24px; }}
.stack-card-lg .metric-card-value {{ font-size: 34px; }}
.stack-card-lg .metric-card-label {{ font-size: 12.5px; }}
.stack-card-lg .metric-card-sub {{ font-size: 12.5px; }}
.stack-card-lg .icon-outline {{ width: 36px; height: 36px; font-size: 15px; }}

.donut-card {{ display: flex; flex-direction: column; }}
.donut-wrap {{ display: flex; align-items: center; justify-content: space-between; gap: 10px; margin-top: 16px; }}
.legend-col {{ display: flex; flex-direction: column; gap: 7px; }}
.legend-row {{ display: flex; align-items: center; gap: 6px; font-size: 11px; color: rgba({TEXT_RGB},.6); }}
.legend-dot {{ width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; }}
.donut-circle {{ width: 76px; height: 76px; border-radius: 50%; position: relative; flex-shrink: 0; }}
.donut-hole {{ position: absolute; top: 50%; left: 50%; transform: translate(-50%,-50%); width: 44px; height: 44px; border-radius: 50%; background: {BG_CARD}; }}

/* Versão "grande" do donut-card: usada quando ele ocupa metade da
   largura da tela (2 colunas) em vez de um quarto (4 colunas). */
.donut-card-lg {{ padding: 26px 28px; }}
.donut-card-lg .metric-card-value {{ font-size: 36px; }}
.donut-card-lg .metric-card-label {{ font-size: 13px; }}
.donut-card-lg .donut-wrap {{ margin-top: 22px; }}
.donut-card-lg .donut-circle {{ width: 130px; height: 130px; }}
.donut-card-lg .donut-hole {{ width: 76px; height: 76px; }}
.donut-card-lg .legend-row {{ font-size: 13px; }}
.donut-card-lg .legend-dot {{ width: 9px; height: 9px; }}

.ring-card-top {{ display: flex; align-items: center; justify-content: space-between; }}
.ring-badge {{ width: 42px; height: 42px; border-radius: 50%; position: relative; flex-shrink: 0; }}
.ring-badge-hole {{
    position: absolute; top: 50%; left: 50%; transform: translate(-50%,-50%);
    width: 31px; height: 31px; border-radius: 50%; background: {BG_CARD};
    display: flex; align-items: center; justify-content: center;
    font-size: 9.5px; font-weight: 700;
}}

/* Versão "grande" do ring-card: usada quando ocupa metade da largura
   (2 colunas) em vez de um quarto. */
.ring-card-lg {{ padding: 26px 28px; }}
.ring-card-lg .icon-outline {{ width: 38px; height: 38px; font-size: 16px; }}
.ring-card-lg .ring-badge {{ width: 60px; height: 60px; }}
.ring-card-lg .ring-badge-hole {{ width: 44px; height: 44px; font-size: 13px; }}
.ring-card-lg .metric-card-label {{ font-size: 13px; margin-top: 18px !important; }}
.ring-card-lg .metric-card-value {{ font-size: 36px; }}
.ring-card-lg .metric-card-sub {{ font-size: 12.5px; }}

.chart-card {{
    background: {BG_CARD}; border: 1px solid {BORDER};
    border-radius: 14px; padding: 20px 22px 8px 22px; margin-bottom: 16px;
}}
.chart-title-row {{ display: flex; align-items: center; justify-content: space-between; }}
.chart-title {{ font-size: 14px; font-weight: 600; color: rgba({TEXT_RGB},.85); }}
.chart-sub {{ font-size: 11px; color: rgba({TEXT_RGB},.4); margin-bottom: 8px; }}
.chart-badge {{ font-size: 11px; color: rgba({TEXT_RGB},.45); background: rgba({TEXT_RGB},.05); padding: 3px 10px; border-radius: 6px; }}

.mini-table {{ width: 100%; border-collapse: collapse; font-size: 12px; }}
.mini-table th {{ text-align: left; font-size: 10.5px; color: rgba({TEXT_RGB},.4); text-transform: uppercase; letter-spacing: .4px; padding: 6px 8px; font-weight: 600; }}
.mini-table td {{ padding: 9px 8px; color: rgba({TEXT_RGB},.75); }}
.mini-table tr {{ border-radius: 8px; }}
.status-chip {{ font-size: 10.5px; font-weight: 600; padding: 3px 10px; border-radius: 999px; display: inline-block; }}

hr {{ border-color: {BORDER} !important; margin: 24px 0 !important; }}
.section-label {{ font-size: 11px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; color: rgba({TEXT_RGB},.4); margin-bottom: 12px; }}
</style>
""", unsafe_allow_html=True)


# ─── Dados ────────────────────────────────────────────────────────────────────
# O sistema exporta o CSV sempre com a data no nome
# (ex: participantes-29_06_2026.csv). Em vez de fixar um nome exato,
# procuramos por esse padrão na pasta e pegamos sempre o arquivo
# mais recente — assim você só precisa jogar o CSV novo na pasta.
PASTA_DADOS  = os.path.dirname(os.path.abspath(__file__))
PADRAO_CSV   = "participantes.csv"


def encontrar_csv_mais_recente(pasta, padrao):
    candidatos = glob.glob(os.path.join(pasta, padrao))
    if not candidatos:
        return None
    # max() com key=os.path.getmtime escolhe pela DATA DE MODIFICAÇÃO real
    # do arquivo no disco, não pelo nome — mais confiável que confiar
    # que o nome do arquivo está sempre formatado igual.
    return max(candidatos, key=os.path.getmtime)


@st.cache_data
def _ler_csv(caminho, mtime):
    """
    'mtime' entra como argumento só pra servir de "chave de cache".
    Sempre que o arquivo for substituído (ou um arquivo mais novo aparecer
    na pasta), o mtime muda → o Streamlit relê o CSV do disco.
    Se nada mudou, usa o resultado em cache sem tocar no disco de novo.
    """
    # encoding="utf-8-sig" remove o BOM (caractere invisível no início do
    # arquivo) que o Excel/sistemas de exportação costumam colocar —
    # sem isso, a primeira coluna viraria "﻿Evento" em vez de "Evento".
    return pd.read_csv(caminho, encoding="utf-8-sig")


def carregar_dados():
    caminho_csv = encontrar_csv_mais_recente(PASTA_DADOS, PADRAO_CSV)

    if caminho_csv is None:
        st.error(
            f"⚠️ Nenhum arquivo encontrado com o padrão `{PADRAO_CSV}` em "
            f"`{PASTA_DADOS}`. Baixe o CSV mais recente do painel e salve "
            "nessa pasta (pode manter o nome original com a data)."
        )
        st.stop()

    mtime = os.path.getmtime(caminho_csv)
    df = _ler_csv(caminho_csv, mtime)
    return df, mtime, caminho_csv


df, ultima_atualizacao, arquivo_usado = carregar_dados()

# ─── Mapeamento das colunas reais do CSV pros nomes que o dashboard usa ──────
# Evento  -> sessao   (as 29 "regiões" do acampamento)
# Idade   -> idade    (já vem numérica, sem conversão necessária)
# Membro  -> membro   (já vem como texto "Sim"/"Nao", só traduzimos o rótulo)
df['sessao'] = df['Evento']
df['idade']  = pd.to_numeric(df['Idade'], errors='coerce')
df['membro'] = df['Membro'].map({"Sim": "Membro", "Nao": "Não Membro"})


# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="brand-block">
        <div class="brand-icon">⛺</div>
        <div class="brand-name">MENU</div>
    </div>
    <div class="nav-section-label"></div>
    """, unsafe_allow_html=True)

    # Navegação real entre páginas: guardamos qual página está ativa no
    # session_state (persiste entre as "reruns" do Streamlit). Os botões
    # abaixo substituem os antigos <div class="nav-item"> decorativos —
    # eles eram só HTML, sem nenhuma ação ligada ao clique.
    if "pagina_atual" not in st.session_state:
        st.session_state.pagina_atual = "Inscricoes"

    def _ir_para_inscricoes():
        st.session_state.pagina_atual = "Inscricoes"

    def _ir_para_participantes():
        st.session_state.pagina_atual = "Participantes"

    # type="primary"/"secondary" no botão controla a aparência: o botão
    # da página ativa fica destacado (estilizado no CSS pra imitar o
    # ".nav-item.active" de antes), o outro fica neutro.
    st.button(
        "📊  Inscrições", on_click=_ir_para_inscricoes, use_container_width=True,
        key="nav_inscricoes",
        type="primary" if st.session_state.pagina_atual == "Inscricoes" else "secondary",
    )
    st.button(
        "👥  Participantes", on_click=_ir_para_participantes, use_container_width=True,
        key="nav_participantes",
        type="primary" if st.session_state.pagina_atual == "Participantes" else "secondary",
    )

    st.markdown("""
    <div class="nav-item"><span class="nav-icon">🗓️</span> Sessões</div>
    <div class="nav-item"><span class="nav-icon">📋</span> Relatórios</div>
    <hr class="sidebar-divider">
    <div class="nav-section-label">Filtros</div>
    """, unsafe_allow_html=True)

    sessoes_disponiveis  = sorted(df['sessao'].dropna().unique())
    tipos_disponiveis    = sorted(df['membro'].unique())

    # Com 29 sessões, "caixinhas" (pills) ficam grandes e difíceis de
    # escanear visualmente. Multiselect resolve melhor aqui porque tem
    # busca por texto embutida (digita "cui" e já filtra "Cuiabá").
    # Pra cobrir o caso "quero tudo de uma vez" sem precisar clicar nas
    # 29 opções manualmente, adiciono 2 botões de atalho acima da lista.
    def _selecionar_todas_sessoes():
        st.session_state.sessoes_multiselect = sessoes_disponiveis

    def _limpar_sessoes():
        st.session_state.sessoes_multiselect = []

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        st.button("Todas", on_click=_selecionar_todas_sessoes, use_container_width=True, key="btn_todas_sessao")
    with col_btn2:
        st.button("Limpar", on_click=_limpar_sessoes, use_container_width=True, key="btn_limpar_sessao")

    sessoes_selecionadas = st.multiselect(
        "Sessão",
        options=sessoes_disponiveis,
        default=[],  # só vale na primeiríssima vez; depois quem manda é o key abaixo
        key="sessoes_multiselect",
        placeholder="Digite ou selecione sessões...",
    )

    st.markdown('<div class="filter-block-divider"></div>', unsafe_allow_html=True)

    # ─── Filtro em cascata: Estaca depende da(s) Sessão(ões) escolhida(s) ────
    # Sempre que a lista de sessões selecionadas mudar, a lista de estacas
    # disponíveis também muda. Em vez de popular a caixa com TODAS as
    # tags (o que fica poluído com 300+ estacas), usamos uma variável de
    # controle escondida (`estacas_modo_todos`): quando ativa, a caixa fica
    # vazia visualmente, mas o filtro por trás considera "todas selecionadas".
    estacas_disponiveis = sorted(
        df.loc[df['sessao'].isin(sessoes_selecionadas), 'Estaca'].dropna().unique()
    ) if sessoes_selecionadas else []

    # Sessão mudou -> reseta a caixa pra vazia e volta pro modo "todas" (silencioso)
    if st.session_state.get("_estacas_opcoes_anteriores") != estacas_disponiveis:
        st.session_state.estacas_multiselect = []
        st.session_state.estacas_modo_todos = True
        st.session_state._estacas_opcoes_anteriores = estacas_disponiveis

    def _selecionar_todas_estacas():
        st.session_state.estacas_multiselect = []   # caixa some vazia
        st.session_state.estacas_modo_todos = True   # mas filtra tudo por trás

    def _limpar_estacas():
        st.session_state.estacas_multiselect = []
        st.session_state.estacas_modo_todos = False  # caixa vazia = filtra nada mesmo

    col_estaca1, col_estaca2 = st.columns(2)
    with col_estaca1:
        st.button("Todas", on_click=_selecionar_todas_estacas, use_container_width=True,
                   key="btn_todas_estaca", disabled=not sessoes_selecionadas)
    with col_estaca2:
        st.button("Limpar", on_click=_limpar_estacas, use_container_width=True,
                   key="btn_limpar_estaca", disabled=not sessoes_selecionadas)

    estacas_marcadas_na_caixa = st.multiselect(
        "Estaca",
        options=estacas_disponiveis,
        key="estacas_multiselect",
        placeholder="Selecione uma sessão primeiro..." if not sessoes_selecionadas else "Digite ou selecione estacas...",
        disabled=not sessoes_selecionadas,
    )
    estacas_marcadas_na_caixa = list(estacas_marcadas_na_caixa or [])

    if estacas_marcadas_na_caixa:
        # Usuário escolheu estacas específicas manualmente -> sai do modo "todas"
        st.session_state.estacas_modo_todos = False
        estacas_selecionadas = estacas_marcadas_na_caixa
    elif st.session_state.get("estacas_modo_todos", True):
        estacas_selecionadas = estacas_disponiveis    # modo "todas" silencioso
    else:
        estacas_selecionadas = []                     # modo "limpar" (nada)

    st.markdown('<div class="filter-block-divider"></div>', unsafe_allow_html=True)

    # ─── Filtro em cascata: Unidade depende da(s) Estaca(s) escolhida(s) ─────
    # Mesma lógica do modo "todos silencioso", um nível mais profundo.
    unidades_disponiveis = sorted(
        df.loc[
            df['sessao'].isin(sessoes_selecionadas) & df['Estaca'].isin(estacas_selecionadas),
            'Unidade'
        ].dropna().unique()
    ) if (sessoes_selecionadas and estacas_selecionadas) else []

    if st.session_state.get("_unidades_opcoes_anteriores") != unidades_disponiveis:
        st.session_state.unidades_multiselect = []
        st.session_state.unidades_modo_todos = True
        st.session_state._unidades_opcoes_anteriores = unidades_disponiveis

    def _selecionar_todas_unidades():
        st.session_state.unidades_multiselect = []
        st.session_state.unidades_modo_todos = True

    def _limpar_unidades():
        st.session_state.unidades_multiselect = []
        st.session_state.unidades_modo_todos = False

    col_unid1, col_unid2 = st.columns(2)
    with col_unid1:
        st.button("Todas", on_click=_selecionar_todas_unidades, use_container_width=True,
                   key="btn_todas_unidade", disabled=not estacas_selecionadas)
    with col_unid2:
        st.button("Limpar", on_click=_limpar_unidades, use_container_width=True,
                   key="btn_limpar_unidade", disabled=not estacas_selecionadas)

    unidades_marcadas_na_caixa = st.multiselect(
        "Unidade",
        options=unidades_disponiveis,
        key="unidades_multiselect",
        placeholder="Selecione uma estaca primeiro..." if not estacas_selecionadas else "Digite ou selecione unidades...",
        disabled=not estacas_selecionadas,
    )
    unidades_marcadas_na_caixa = list(unidades_marcadas_na_caixa or [])

    if unidades_marcadas_na_caixa:
        st.session_state.unidades_modo_todos = False
        unidades_selecionadas = unidades_marcadas_na_caixa
    elif st.session_state.get("unidades_modo_todos", True):
        unidades_selecionadas = unidades_disponiveis
    else:
        unidades_selecionadas = []

    st.markdown('<div class="filter-block-divider"></div>', unsafe_allow_html=True)

    # Tipo (Membro/Não Membro) continua como pills — só 2 opções, então
    # o problema de espaço/escaneamento visual não existe aqui.
    if hasattr(st, "pills"):
        tipo_participante = st.pills(
            "Tipo",
            options=tipos_disponiveis,
            selection_mode="multi",
            default=tipos_disponiveis,
        )
    else:
        tipo_participante = st.multiselect("Tipo", tipos_disponiveis, default=tipos_disponiveis)

    tipo_participante = list(tipo_participante or [])

    # Espaço um pouco maior aqui — separa visualmente os filtros de
    # "quem" (Sessão/Estaca/Unidade/Tipo) do filtro de "idade", que é
    # uma categoria conceitualmente diferente.
    st.markdown('<div class="filter-block-divider" style="margin-top:28px;"></div>', unsafe_allow_html=True)

    # Mesmo padrão usado em "Sessão": multiselect (idades específicas,
    # 18 a 35 — faixa permitida no acampamento) + botões de atalho
    # "Todas" e "Limpar", começando sem nenhuma marcada.
    idades_disponiveis = list(range(17, 36))  # 17, 18, ..., 35

    def _selecionar_todas_idades():
        st.session_state.idades_multiselect = idades_disponiveis

    def _limpar_idades():
        st.session_state.idades_multiselect = []

    col_idade1, col_idade2 = st.columns(2)
    with col_idade1:
        st.button("Todas", on_click=_selecionar_todas_idades, use_container_width=True, key="btn_todas_idade")
    with col_idade2:
        st.button("Limpar", on_click=_limpar_idades, use_container_width=True, key="btn_limpar_idade")

    idades_selecionadas = st.multiselect(
        "Idade",
        options=idades_disponiveis,
        default=[],
        key="idades_multiselect",
        placeholder="Selecione idades...",
    )
    idades_selecionadas = list(idades_selecionadas or [])

    st.markdown("""
    <div class="support-card">
        <div class="support-icon">🏕️</div>
        <div class="support-title">Precisa de ajuda?</div>
        <div class="support-text">Fale com a coordenação do acampamento sobre dúvidas nas inscrições.</div>
        <span class="support-btn">Contato</span>
    </div>
    """, unsafe_allow_html=True)

    # Indicador de frescor do dado: mostra qual arquivo está sendo usado
    # e quando ele foi modificado de verdade no disco.
    hora_fmt = datetime.datetime.fromtimestamp(ultima_atualizacao).strftime("%d/%m/%Y %H:%M:%S")
    nome_arquivo = os.path.basename(arquivo_usado)
    st.markdown(
        f'<div style="padding:10px 20px;font-size:11px;color:rgba({TEXT_RGB},.45);">'
        f'📄 Arquivo: <b>{nome_arquivo}</b><br>'
        f'🕒 Atualizado em: <b>{hora_fmt}</b></div>',
        unsafe_allow_html=True,
    )


# ─── Filtro ───────────────────────────────────────────────────────────────────
df_f = df[
    (df['sessao'].isin(sessoes_selecionadas)) &
    (df['Estaca'].isin(estacas_selecionadas)) &
    (df['Unidade'].isin(unidades_selecionadas)) &
    (df['membro'].isin(tipo_participante)) &
    (df['idade'].isin(idades_selecionadas))
]

total       = df_f.shape[0]
media_idade = df_f['idade'].mean() if not df_f.empty else 0
maior_idade = int(df_f['idade'].max()) if not df_f.empty else 0
nao_membros = df_f[df_f['membro'] == "Não Membro"].shape[0]
membros     = df_f[df_f['membro'] == "Membro"].shape[0]
pct_membros = (membros / total * 100) if total > 0 else 0

aprovados      = df_f[df_f['Aprovado'] == "Sim"].shape[0]
confirmados    = df_f[df_f['Confirmado'] == "Sim"].shape[0]
pct_aprovados  = (aprovados / total * 100) if total > 0 else 0
pct_confirmados = (confirmados / total * 100) if total > 0 else 0

LAYOUT = dict(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font_color=f"rgba({TEXT_RGB},0.65)",
    font_size=12,
    margin=dict(t=10, b=10, l=10, r=10),
    showlegend=False,
)


if st.session_state.pagina_atual == "Inscricoes":
    # ─── Header ───────────────────────────────────────────────────────────────────
    hc1, hc2 = st.columns([3, 2])
    with hc1:
        st.markdown("""
        <div class="page-title">Inscrições</div>
        <div class="page-subtitle">Análise geral dos participantes do acampamento</div>
        """, unsafe_allow_html=True)
    with hc2:
        st.markdown("""
        <div class="header-right" style="justify-content:flex-end; margin-top:6px;">
            <div class="date-pill"> 2026</div>
            <div class="avatar-group">
                <span class="avatar-name">CJAS - 2026</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom:18px'></div>", unsafe_allow_html=True)

    if total == 0:
        if len(sessoes_selecionadas) == 0 and len(idades_selecionadas) == 0:
            st.info("👈 Selecione sessões e idades na barra lateral (ou clique em **Todas**) pra ver os dados.")
        elif len(sessoes_selecionadas) == 0:
            st.info("👈 Selecione uma ou mais sessões na barra lateral (ou clique em **Todas**) pra ver os dados.")
        elif len(idades_selecionadas) == 0:
            st.info("👈 Selecione uma ou mais idades na barra lateral (ou clique em **Todas**) pra ver os dados.")
        else:
            st.info("Nenhum participante encontrado com essa combinação de filtros.")


    # ─── Linha A: 4 cards grandes em cima (lado a lado) ──────────────────────────
    colA1, colA2, colA3, colA4 = st.columns(4)

    with colA1:
        st.markdown(stack_card_html("📋", "TOTAL INSCRITOS", str(total), "participantes no filtro", BRAND_LIGHT, grande=True), unsafe_allow_html=True)

    with colA2:
        st.markdown(stack_card_html("🎂", "IDADE MÉDIA", f"{media_idade:.1f}", "anos, em média", ACCENT_GOLD, grande=True), unsafe_allow_html=True)

    with colA3:
        st.markdown(stack_card_html("📈", "MAIOR IDADE", str(maior_idade), "anos registrados", ACCENT_SAGE, grande=True), unsafe_allow_html=True)

    with colA4:
        st.markdown(stack_card_html("🆕", "NÃO MEMBROS", str(nao_membros), f"{100-pct_membros:.0f}% do total", ACCENT_RUST, grande=True), unsafe_allow_html=True)

    # Espaço entre a fileira de cima (4 cards) e a de baixo (2 donuts)
    st.markdown("<div style='margin-bottom:18px'></div>", unsafe_allow_html=True)

    # ─── Linha A.2: os 2 donuts, maiores, lado a lado embaixo ───────────────────
    colA5, colA6 = st.columns(2)

    with colA5:
        if total > 0:
            contagem_sessao = df_f['sessao'].value_counts(normalize=True).mul(100)
            if len(contagem_sessao) <= 3:
                segs = list(contagem_sessao.items())
            else:
                segs = list(contagem_sessao.iloc[:2].items()) + [("Outras", contagem_sessao.iloc[2:].sum())]
            cores_segs = [BRAND_LIGHT, ACCENT_GOLD, ACCENT_SAGE][:len(segs)]
            legend_items = [(nome, p, cor) for (nome, p), cor in zip(segs, cores_segs)]
            donut_segments = [(p, cor) for (_, p), cor in zip(segs, cores_segs)]
            st.markdown(
                donut_card_html("INSCRITOS POR SESSÃO", str(total), "no filtro atual", legend_items, donut_segments, grande=True),
                unsafe_allow_html=True,
            )
        else:
            st.markdown(donut_card_html("INSCRITOS POR SESSÃO", "0", "sem dados no filtro", [], [(100, BORDER)], grande=True), unsafe_allow_html=True)

    with colA6:
        if total > 0:
            legend_items = [("Membros", pct_membros, BRAND_LIGHT), ("Não Membros", 100 - pct_membros, TAUPE)]
            donut_segments = [(pct_membros, BRAND_LIGHT), (100 - pct_membros, TAUPE)]
            st.markdown(
                donut_card_html("MEMBROS", str(membros), f"{pct_membros:.0f}% do total filtrado", legend_items, donut_segments, grande=True),
                unsafe_allow_html=True,
            )
        else:
            st.markdown(donut_card_html("MEMBROS", "0", "sem dados no filtro", [], [(100, BORDER)], grande=True), unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom:16px'></div>", unsafe_allow_html=True)


    # ─── Linha B.1: cards de Aprovados e Confirmados, lado a lado ────────────────
    colB1, colB2 = st.columns(2)

    with colB1:
        st.markdown(
            ring_card_html(
                "✅", "APROVADOS", str(aprovados),
                f"de {total} inscritos no filtro",
                pct_aprovados, BRAND_LIGHT, grande=True,
            ),
            unsafe_allow_html=True,
        )

    with colB2:
        st.markdown(
            ring_card_html(
                "🗳️", "CONFIRMADOS", str(confirmados),
                f"de {total} inscritos no filtro",
                pct_confirmados, ACCENT_SAGE, grande=True,
            ),
            unsafe_allow_html=True,
        )

    # Separador entre o bloco de cards e o gráfico (mesmo espaçamento usado
    # nos filtros da sidebar, agora aplicado ao conteúdo principal)
    st.markdown("<hr style='margin: 24px 0;'>", unsafe_allow_html=True)

    # ─── Linha B.2: gráfico de barras HORIZONTAL, largura total ──────────────────
    # Por que horizontal em vez de vertical: com 29 sessões e nomes longos
    # (ex: "Rio de Janeiro Norte e Rio de Janeiro Sul"), barras verticais
    # obrigam a girar o texto a 90° — difícil de ler. Na horizontal, os
    # nomes ficam na lateral, na horizontal normal de leitura, e ainda
    # sobra mais espaço pra cada barra respirar.
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown("""
    <div class="chart-title-row">
        <div class="chart-title">Inscrições por Sessão</div>
        <div class="chart-badge">2026 ⌄</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<div class="chart-sub">Quantidade de inscritos em cada sessão</div>', unsafe_allow_html=True)
    if not df_f.empty:
        contagem = df_f['sessao'].value_counts().reset_index()
        contagem.columns = ['sessao', 'quantidade']
        contagem = contagem.sort_values('quantidade', ascending=False)

        fig = px.bar(contagem, x='quantidade', y='sessao', orientation='h',
                     color_discrete_sequence=[BRAND_LIGHT])
        fig.update_traces(marker_line_width=0)
        fig.update_layout(
            **LAYOUT,
            height=max(320, len(contagem) * 24),  # cresce com o nº de sessões, sem amontoar
            xaxis=dict(title="", showgrid=True, gridcolor=f"rgba({TEXT_RGB},0.08)"),
            yaxis=dict(title="", autorange="reversed"),  # maior sessão fica no topo
        )
        st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom:16px'></div>", unsafe_allow_html=True)


    # ─── Linha C: mini-tabela de últimos inscritos (largura total) ──────────────
    st.markdown('<div class="chart-card" style="padding-bottom:14px;">', unsafe_allow_html=True)
    st.markdown("""
    <div class="chart-title-row">
        <div class="chart-title">Últimos Inscritos</div>
        <div class="chart-badge">⟳</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<div class="chart-sub">Prévia dos participantes no filtro atual</div>', unsafe_allow_html=True)

    if not df_f.empty:
        linhas_html = ""
        # Agora que a tabela ocupa a largura toda (em vez de meia coluna),
        # vale mostrar mais linhas pra aproveitar o espaço — subi de 6 pra 10.
        for i, row in df_f.head(10).reset_index(drop=True).iterrows():
            is_membro = row['membro'] == "Membro"
            chip_bg = "rgba(139,90,60,.14)" if is_membro else "rgba(201,184,163,.30)"
            chip_color = BRAND_LIGHT if is_membro else "#7A6A55"
            linhas_html += (
                "<tr>"
                f"<td>#{i+1:03d}</td>"
                f"<td>{row['sessao']}</td>"
                f"<td>{int(row['idade'])} anos</td>"
                f'<td><span class="status-chip" style="background:{chip_bg};color:{chip_color};">{row["membro"]}</span></td>'
                "</tr>"
            )
        tabela_html = (
            '<table class="mini-table">'
            "<thead><tr><th>Nº</th><th>Sessão</th><th>Idade</th><th>Status</th></tr></thead>"
            f"<tbody>{linhas_html}</tbody>"
            "</table>"
        )
        st.markdown(tabela_html, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)



elif st.session_state.pagina_atual == "Participantes":
    # ─── Página: Participantes (lista completa filtrada) ─────────────────────────
    hc1, hc2 = st.columns([3, 2])
    with hc1:
        st.markdown("""
        <div class="page-title">Participantes</div>
        <div class="page-subtitle">Lista completa de inscritos no filtro atual</div>
        """, unsafe_allow_html=True)
    with hc2:
        st.markdown("""
        <div class="header-right" style="justify-content:flex-end; margin-top:6px;">
            <div class="date-pill">2026</div>
            <div class="avatar-group">
                <div class="avatar-circle">P</div>
                <span class="avatar-name">Participantes</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom:18px'></div>", unsafe_allow_html=True)

    if total == 0:
        st.info("Nenhum participante encontrado com os filtros atuais.")

    st.markdown(f'<div class="section-label">{total} participantes no filtro atual</div>', unsafe_allow_html=True)
    st.dataframe(df_f, use_container_width=True, hide_index=True, height=600)