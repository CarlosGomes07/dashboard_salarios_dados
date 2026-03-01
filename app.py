import streamlit as st
import pandas as pd
import plotly.express as px

# --- Configuração da Página ---
st.set_page_config(
    page_title="Dashboard de Salários na Área de Dados",
    page_icon="📊",
    layout="wide",
)

# --- Carregamento dos dados com Cache ---
# O decorador cache_data evita que o arquivo seja lido do disco a cada interação.
@st.cache_data
def load_data(file_path):
    df = pd.read_csv(file_path)
    # Convertendo colunas categóricas para economizar memória (opcional, mas bom para performance)
    df['ano'] = df['ano'].astype(int)
    return df

try:
    df = load_data("dados-imersao.csv")
except FileNotFoundError:
    st.error("Arquivo 'dados-imersao.csv' não encontrado. Verifique o caminho.")
    st.stop()

# --- Barra Lateral (Filtros) ---
st.sidebar.header("🔍 Filtros")

# Centralizamos a lógica de seleção de filtros únicos para ganhar performance
anos_disponiveis = sorted(df['ano'].unique())
senioridades_disponiveis = sorted(df['senioridade'].unique())
contratos_disponiveis = sorted(df['contrato'].unique())
tamanhos_disponiveis = sorted(df['tamanho_empresa'].unique())

anos_selecionados = st.sidebar.multiselect("Ano", anos_disponiveis, default=anos_disponiveis)
senioridades_selecionadas = st.sidebar.multiselect("Senioridade", senioridades_disponiveis, default=senioridades_disponiveis)
contratos_selecionados = st.sidebar.multiselect("Tipo de Contrato", contratos_disponiveis, default=contratos_disponiveis)
tamanhos_selecionados = st.sidebar.multiselect("Tamanho da Empresa", tamanhos_disponiveis, default=tamanhos_disponiveis)

# --- Filtragem do DataFrame ---
df_filtrado = df[
    (df['ano'].isin(anos_selecionados)) &
    (df['senioridade'].isin(senioridades_selecionadas)) &
    (df['contrato'].isin(contratos_selecionados)) &
    (df['tamanho_empresa'].isin(tamanhos_selecionados))
]

# --- Conteúdo Principal ---
st.title("🎲 Dashboard de Análise de Salários na Área de Dados")
st.markdown("Explore os dados salariais na área de dados. Utilize os filtros à esquerda.")

# --- Métricas Principais (KPIs) ---
st.subheader("Métricas gerais (Salário anual em USD)")

if not df_filtrado.empty:
    salario_medio = df_filtrado['usd'].mean()
    salario_maximo = df_filtrado['usd'].max()
    total_registros = df_filtrado.shape[0]
    cargo_mais_frequente = df_filtrado["cargo"].mode()[0]
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Salário médio", f"${salario_medio:,.0f}")
    col2.metric("Salário máximo", f"${salario_maximo:,.0f}")
    col3.metric("Total de registros", f"{total_registros:,}")
    col4.metric("Cargo mais frequente", cargo_mais_frequente)
else:
    st.warning("Nenhum dado disponível para os filtros selecionados.")

st.markdown("---")

# --- Análises Visuais ---
st.subheader("Gráficos")

if not df_filtrado.empty:
    col_graf1, col_graf2 = st.columns(2)

    with col_graf1:
        top_cargos = df_filtrado.groupby('cargo')['usd'].mean().nlargest(10).sort_values(ascending=True).reset_index()
        grafico_cargos = px.bar(
            top_cargos, x='usd', y='cargo', orientation='h',
            title="Top 10 cargos por salário médio",
            labels={'usd': 'Média salarial (USD)', 'cargo': ''}
        )
        st.plotly_chart(grafico_cargos, use_container_width=True)

    with col_graf2:
        grafico_hist = px.histogram(
            df_filtrado, x='usd', nbins=30,
            title="Distribuição de salários anuais",
            labels={'usd': 'Faixa salarial (USD)'}
        )
        st.plotly_chart(grafico_hist, use_container_width=True)

    col_graf3, col_graf4 = st.columns(2)

    with col_graf3:
        remoto_contagem = df_filtrado['remoto'].value_counts().reset_index()
        remoto_contagem.columns = ['tipo_trabalho', 'quantidade']
        grafico_remoto = px.pie(
            remoto_contagem, names='tipo_trabalho', values='quantidade',
            title='Proporção dos tipos de trabalho', hole=0.5
        )
        st.plotly_chart(grafico_remoto, use_container_width=True)

    with col_graf4:
        df_ds = df_filtrado[df_filtrado['cargo'] == 'Data Scientist']
        if not df_ds.empty:
            media_ds_pais = df_ds.groupby('residencia_iso3')['usd'].mean().reset_index()
            grafico_paises = px.choropleth(
                media_ds_pais, locations='residencia_iso3', color='usd',
                color_continuous_scale='rdylgn', title='Salário Médio de DS por País'
            )
            st.plotly_chart(grafico_paises, use_container_width=True)
        else:
            st.info("Filtre por 'Data Scientist' para ver o mapa.")

# --- Tabela de Dados ---
st.subheader("Dados Detalhados")
st.dataframe(df_filtrado, use_container_width=True)