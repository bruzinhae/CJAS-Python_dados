import streamlit as st

st.set_page_config(
    page_title="Acampamento CJAS 2026",
    page_icon="🏕️",
    layout="wide"
)

st.markdown("""
<style>

.stApp {
    background: linear-gradient(180deg, #1b4332, #2d6a4f, #40916c);
    color: white;
    font-family: 'Segoe UI', sans-serif;
}

/* Título principal */
.main-title {
    text-align: center;
    font-size: 50px;
    font-weight: 800;
    margin-bottom: 5px;
}

.subtitle {
    text-align: center;
    font-size: 18px;
    opacity: 0.9;
    margin-bottom: 40px;
}

/* Cards estilo natureza */
.card {
    background: rgba(255, 255, 255, 0.08);
    backdrop-filter: blur(8px);
    padding: 25px;
    border-radius: 20px;
    border: 1px solid rgba(255,255,255,0.15);
    transition: 0.3s ease;
    text-align: center;
}

.card:hover {
    transform: translateY(-8px);
    box-shadow: 0 0 20px rgba(255,255,255,0.3);
}

.big-number {
    font-size: 36px;
    font-weight: bold;
    margin-bottom: 8px;
}

/* Barra lateral */
section[data-testid="stSidebar"] {
    background-color: #081c15;
}

/* Botão personalizado */
div.stButton > button {
    background-color: #d8f3dc;
    color: #081c15;
    border-radius: 25px;
    padding: 0.6rem 1.8rem;
    border: none;
    font-weight: bold;
}

div.stButton > button:hover {
    background-color: #b7e4c7;
}

</style>
""", unsafe_allow_html=True)


st.markdown('<div class="main-title">🏕️ Acampamento JAS 2026</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Painel de Controle de Inscrições</div>', unsafe_allow_html=True)

st.markdown("---")


col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="card">
        <div class="big-number">87</div>
        Inscritos
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="card">
        <div class="big-number">120</div>
        Vagas Totais
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="card">
        <div class="big-number">78</div>
        Pagamentos Confirmados
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="card">
        <div class="big-number">12</div>
        Restrições Alimentares
    </div>
    """, unsafe_allow_html=True)




st.subheader("📊 Visão Geral")

col5, col6 = st.columns(2)

with col5:
    st.markdown("""
    <div class="card">
        <h4>Inscritos por Sessão</h4>
        <p>(Gráfico aparecerá aqui)</p>
    </div>
    """, unsafe_allow_html=True)

with col6:
    st.markdown("""
    <div class="card">
        <h4>Situação de Pagamento</h4>
        <p>(Gráfico aparecerá aqui)</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("  ")

col7, col8 = st.columns(2)

with col7:
    st.markdown("""
    <div class="card">
        <h4>Membros e não membros</h4>
        <p>Gráfico aqui</p>
    </div>
    """, unsafe_allow_html=True)

with col8:
    st.markdown("""
    <div class="card">
        <h4>Distribuição por Idade</h4>
        <p>(Gráfico aparecerá aqui)</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")


st.sidebar.header("🔍 Filtros")

st.sidebar.multiselect("Sessão", ["Campinas", "São Paulo Norte", "São Paulo Sul"])
st.sidebar.selectbox("Sexo", ["Masculino", "Feminino"])
st.sidebar.selectbox("Pagamento", ["Pago", "Pendente", "Parcial"])
st.sidebar.checkbox("Somente com restrição alimentar")
st.sidebar.checkbox("Somente quem vai de ônibus")


st.subheader("📑 Lista de Inscritos")

st.dataframe(
    {
        "Nome": ["João Silva", "Maria Souza", "Lucas Almeida"],
        "Idade": [18, 19, 20],
        "Sessão": ["Campinas", "São Paulo Norte", "São Paulo Sul"],
        "Pagamento": ["Pago", "Pendente", "Pago"],
        "Transporte": ["Ônibus", "Próprio", "Ônibus"]
    }
)

st.markdown("""
<hr style="border: 1px solid rgba(255,255,255,0.2)">
<center>
Sistema interno • Acampamento CJAS 2026 🌲
</center>
""", unsafe_allow_html=True)