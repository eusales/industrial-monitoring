import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time
from data.simulated_data import gerar_dados
from config.settings import LIMITES, DASHBOARD
from notifications import notificar_alerta

# =========================
# Configuração da página
# =========================
st.set_page_config(
    page_title="Dashboard de Monitoramento Industrial",
    layout="wide"
)

st.title("Dashboard de Monitoramento Industrial")

# =========================
# Sidebar - Controles
# =========================
st.sidebar.header("Configurações")
taxa_atualizacao = st.sidebar.slider("Taxa de atualização (segundos)", 1, 10, DASHBOARD["taxa_atualizacao_padrao"])
janela_mm = st.sidebar.slider("Janela da média móvel (amostras)", 3, 20, DASHBOARD["janela_mm_padrao"])

# =========================
# Estados da aplicação
# =========================
if "historico" not in st.session_state:
    st.session_state.historico = pd.DataFrame()
if "pausar_historico" not in st.session_state:
    st.session_state.pausar_historico = False
if "eventos" not in st.session_state:
    st.session_state.eventos = pd.DataFrame(columns=["timestamp", "variavel", "valor", "nivel"])
if "estado_variaveis" not in st.session_state:
    st.session_state.estado_variaveis = {}


# =========================
# Geração de dados
# =========================
df_novo = gerar_dados()
if not st.session_state.pausar_historico:
    st.session_state.historico = pd.concat([st.session_state.historico, df_novo], ignore_index=True)
    if len(st.session_state.historico) > DASHBOARD["historico_maximo"]:
        st.session_state.historico = st.session_state.historico.iloc[-DASHBOARD["historico_maximo"]:]

# =========================
# KPIs coloridos
# =========================
def cor_kpi(valor, var):
    alerta = LIMITES[var].get("alerta", 0)
    critico = LIMITES[var].get("critico", alerta*1.3)
    if valor > critico:
        return "red"
    elif valor > alerta:
        return "orange"
    else:
        return "green"

temp, press, corr, tens, prod, status = df_novo.iloc[0][["temperatura", "pressao", "corrente", "tensao", "producao", "status"]]
st.subheader("KPIs em Tempo Real")
k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("Temperatura (°C)", temp, delta=None, delta_color="normal" if temp < LIMITES["temperatura"]["alerta"] else "inverse")
k2.metric("Pressão (bar)", press)
k3.metric("Corrente (A)", corr)
k4.metric("Tensão (V)", tens)
k5.metric("Produção (pç/h)", prod)
k6.metric("Status", status)

# =========================
# Média móvel
# =========================
if len(st.session_state.historico) >= janela_mm:
    for var in ["temperatura","pressao","corrente","tensao","producao"]:
        st.session_state.historico[f"{var}_mm"] = st.session_state.historico[var].rolling(window=janela_mm).mean()

# =========================
# Registrar eventos
# =========================
def registrar_evento(variavel, valor, nivel):
    eventos = st.session_state.eventos

    novo_evento = {
        "timestamp": pd.Timestamp.now(),
        "variavel": variavel,
        "valor": round(valor, 2),
        "nivel": nivel
    }

    eventos = pd.concat(
        [eventos, pd.DataFrame([novo_evento])],
        ignore_index=True
    )

    # FIFO de eventos (máx. 1000)
    if len(eventos) > DASHBOARD["historico_maximo"]:
        eventos = eventos.iloc[-DASHBOARD["historico_maximo"]:]

    st.session_state.eventos = eventos


# =========================
# Alarmes visuais com notificações
# =========================
st.subheader("Alarmes Industriais")

for var in ["temperatura", "pressao", "corrente", "tensao", "producao"]:

    if f"{var}_mm" not in st.session_state.historico.columns:
        continue

    valor_atual = st.session_state.historico[f"{var}_mm"].iloc[-1]
    limites = LIMITES[var]

    alerta = limites["alerta"]
    critico = limites["critico"]

    if valor_atual > critico:
        nivel_atual = "CRITICO"
        st.error(f"⚠ {var.capitalize()} CRÍTICO (média móvel)")

    elif valor_atual > alerta:
        nivel_atual = "ALERTA"
        st.warning(f"⚠ {var.capitalize()} em nível de alerta")

    else:
        nivel_atual = "NORMAL"

    nivel_anterior = st.session_state.estado_variaveis.get(var)

    # Só registra se mudou de estado
    if nivel_anterior != nivel_atual:

        if nivel_atual != "NORMAL":
            registrar_evento(var, valor_atual, nivel_atual)
            notificar_alerta(var, valor_atual, nivel_atual)

        st.session_state.estado_variaveis[var] = nivel_atual


# =========================
# Gráficos interativos com faixas
# =========================
st.subheader("Gráficos em Tempo Real")
cores = {"temperatura":["green","yellow","red"],"pressao":["green","yellow","red"],"corrente":["green","yellow","red"],"tensao":["green","yellow","red"],"producao":["green","yellow","red"]}

def add_faixas(fig,var):
    limites = LIMITES[var]
    alerta = limites.get("alerta", limites.get("critico", limites["max"]*0.7))
    critico = limites.get("critico", limites["max"])
    fig.add_hrect(y0=0,y1=alerta,fillcolor=cores[var][0],opacity=0.1,line_width=0)
    fig.add_hrect(y0=alerta,y1=critico,fillcolor=cores[var][1],opacity=0.15,line_width=0)
    fig.add_hrect(y0=critico,y1=limites["max"],fillcolor=cores[var][2],opacity=0.15,line_width=0)
    return fig

linha1=["temperatura","pressao","corrente"]
linha2=["tensao","producao"]

cols=st.columns(3)
for i,var in enumerate(linha1):
    y_vars=[var]
    if f"{var}_mm" in st.session_state.historico.columns:
        y_vars.append(f"{var}_mm")
    fig=px.line(st.session_state.historico,x="timestamp",y=y_vars,title=f"{var.capitalize()}")
    fig=add_faixas(fig,var)
    with cols[i]:
        st.plotly_chart(fig,use_container_width=True)

cols=st.columns(2)
for i,var in enumerate(linha2):
    y_vars=[var]
    if f"{var}_mm" in st.session_state.historico.columns:
        y_vars.append(f"{var}_mm")
    fig=px.line(st.session_state.historico,x="timestamp",y=y_vars,title=f"{var.capitalize()}")
    fig=add_faixas(fig,var)
    with cols[i]:
        st.plotly_chart(fig,use_container_width=True)

# =========================
# Pausar histórico
# =========================
st.markdown("---")
if st.button("⏸ Pausar / Retomar Histórico"):
    st.session_state.pausar_historico = not st.session_state.pausar_historico
if st.session_state.pausar_historico:
    st.info("Histórico pausado. KPIs continuam atualizando.")

# =========================
# Logs de eventos recentes
# =========================
st.subheader("Logs de Alarmes Recentes")
st.dataframe(st.session_state.eventos.tail(10))

# =========================
# Loop de atualização
# =========================
time.sleep(taxa_atualizacao)
st.rerun()
