import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA
# ---------------------------------------------------

st.set_page_config(
    page_title="Análise de Cotas",
    layout="wide"
)

st.title("Análise de Cotas Médias")

# ---------------------------------------------------
# CONEXÃO E LEITURA
# ---------------------------------------------------

@st.cache_data
def carregar_dados_cota():

    df = pd.read_parquet("Cotas.parquet")
    
    colunas_cotas = [
        f"Cota{i:02d}" for i in range(1, 32)
    ]

    # converter data
    df["Data"] = pd.to_datetime(df["Data"])
    df["Data"] = df["Data"].dt.strftime("%m/%Y")

    # converter cotas para número
    for c in colunas_cotas:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    # média das cotas
    df["Media_Cotas"] = df[colunas_cotas].mean(axis=1).round(2)

    # ajustar tipos
    df["RegistroID"] = (
        pd.to_numeric(df["RegistroID"], errors="coerce")
        .astype("Int64")
        .astype(str)
    )

    df["CodigoFlu"] = (
        pd.to_numeric(df["CodigoFlu"], errors="coerce")
        .astype("Int64")
        .astype(str)
    )

    return df

df = carregar_dados_cota()


# ---------------------------------------------------
# FILTROS
# ---------------------------------------------------

st.sidebar.header("Filtros")

# regional
regional = st.sidebar.selectbox(
    "Regional",
    ["Todas"] + sorted(df["OperadoraUnidadeSigla"].dropna().unique())
)

# filtrar regional
if regional != "Todas":
    df = df[df["OperadoraUnidadeSigla"] == regional]

# código da estação
codigo = st.sidebar.selectbox(
    "Código da estação",
    ["Todos"] + sorted(df["CodigoFlu"].dropna().unique())
)

if codigo != "Todos":
    df = df[df["CodigoFlu"] == codigo]

# nome da estação
nome = st.sidebar.selectbox(
    "Nome da estação",
    ["Todos"] + sorted(df["Nome"].dropna().unique())
)

if nome != "Todos":
    df = df[df["Nome"] == nome]

# ---------------------------------------------------
# BOXPLOT
# ---------------------------------------------------

fig_box = px.box(
    df,
    y="Media_Cotas",
    points="outliers",
    hover_data=[
        "Data",
        "CodigoFlu",
        "Nome",
        "OperadoraUnidadeSigla"],
    title=f"Boxplot das Cotas Médias da Estação {codigo} ({nome}) - {regional}"
)

fig_box.update_layout(
    xaxis_title="Estação ",
    yaxis_title="Média das Cotas"
)

fig_box.update_traces(
    hovertemplate=
    "<b>Data:</b> %{customdata[0]}<br>" +
    "<b>Média:</b> %{y:.2f}<br>" +
    "<b>Código:</b> %{customdata[1]}<br>" +
    "<b>Estação:</b> %{customdata[2]}<br>" +
    "<b>Regional:</b> %{customdata[3]}<extra></extra>"
)

st.plotly_chart(
    fig_box,
    use_container_width=True
)

# ---------------------------------------------------
# SÉRIE TEMPORAL
# ---------------------------------------------------

fig_line = px.line(
    df.sort_values("Data"),
    x="Data",
    y="Media_Cotas",
    color="CodigoFlu",
    title=f"Série Temporal de cotas médias da estação {codigo}"
)

st.plotly_chart(
    fig_line,
    use_container_width=True
)

# ---------------------------------------------------
# TABELA
# ---------------------------------------------------

st.subheader("Dados dos Outliers")

Q1 = df["Media_Cotas"].quantile(0.25)
Q3 = df["Media_Cotas"].quantile(0.75)

IQR = Q3 - Q1

limite_inferior = Q1 - 1.5 * IQR
limite_superior = Q3 + 1.5 * IQR

df_outliers = df[
    (df["Media_Cotas"] < limite_inferior) |
    (df["Media_Cotas"] > limite_superior)
]

st.dataframe(
    df_outliers[
        [
            "Data",
            "CodigoFlu",
            "Nome",
            "OperadoraUnidadeSigla",
            "Media_Cotas"
        ]
    ]
    .sort_values("Media_Cotas", ascending=False),
    use_container_width=True
)