import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
import streamlit as st
import plotly.express as px
from utils.flags import flags
from utils.team_colors import team_colors

# ======================
# Funções auxiliares
# ======================

@st.cache_data
def load_data():
    results = pd.read_csv("data/results.csv")
    drivers = pd.read_csv("data/drivers.csv")
    races = pd.read_csv("data/races.csv")  # contém ano e nome da corrida
    constructors = pd.read_csv("data/constructors.csv")

    # junta ano e corrida dentro de results
    results = results.merge(races[["raceId", "year", "name"]], on="raceId", how="left")

    return results, drivers, constructors


@st.cache_data
def load_constructor_standings():
    cs = pd.read_csv("data/constructor_standings.csv")
    races = pd.read_csv("data/races.csv")[["raceId", "year"]]
    constructors = pd.read_csv("data/constructors.csv")[["constructorId", "name"]]
    cs = cs.merge(races, on="raceId", how="left").merge(constructors, on="constructorId", how="left")
    return cs

def get_driver_names(drivers_df):
    return drivers_df.set_index("driverId").apply(
        lambda x: f"{x['forename']} {x['surname']}", axis=1
    )


# ======================
# App Streamlit
# ======================

st.set_page_config(page_title="Formula 1 Data Analytics", layout="wide")
st.title("Formula 1 Data Analytics 1950-2024")

# Carregar dados
df, pilots_df, constructors_df = load_data()
cs_df = load_constructor_standings()

# Map driverId -> Nome completo
driver_names = get_driver_names(pilots_df)

# ======================
# Filtros
# ======================
st.sidebar.header("🔍 Filtros")
years = sorted(df["year"].unique())
selected_year = st.sidebar.selectbox("Selecione o ano", ["Todos"] + years)

# Criar cópias separadas
df_completo = df.copy()      # mantém todos os anos
df_filtrado = df.copy()

# Filtrar por ano apenas no df_filtrado
if selected_year != "Todos":
    df_filtrado = df_filtrado[df_filtrado["year"] == selected_year]


# Abas para organizar Pilotos e Equipes/Construtores
tab_pilotos, tab_equipes = st.tabs(["Pilotos", "Equipes/Construtores"])

# ======================
# Top 10 Pilotos
# ======================
with tab_pilotos:
    st.subheader("🏆 Top 10 Pilotos com mais vitórias")

    winners = df_filtrado[df_filtrado["position"] == "1"]
    wins_by_drivers = winners["driverId"].value_counts().head(10)
    wins_by_drivers.index = wins_by_drivers.index.map(driver_names)

    wins_df = wins_by_drivers.reset_index()
    wins_df.columns = ["Piloto", "Vitórias"]

    fig = px.bar(
        wins_df,
        x="Piloto",
        y="Vitórias",
        text="Vitórias",
        # Sem degradê: uma única cor para todas as barras
        color_discrete_sequence=["#4C78A8"],
    )
    st.plotly_chart(fig, use_container_width=True)


# ======================
# Nacionalidades
# ======================
with tab_pilotos:
    st.subheader("🌍 Vitórias por Nacionalidade")

    nationalities = pilots_df.set_index("driverId")["nationality"]
    wins_by_nationalities = winners["driverId"].map(nationalities).value_counts()
    wins_by_nationalities.index = wins_by_nationalities.index.map(
        lambda x: f"{flags.get(x, '')} {x}"
    )

    nat_df = wins_by_nationalities.reset_index()
    nat_df.columns = ["Nacionalidade", "Vitórias"]

    fig = px.bar(
        nat_df,
        x="Nacionalidade",
        y="Vitórias",
        text="Vitórias",
        # Sem degradê: uma única cor para todas as barras
        color_discrete_sequence=["#72B7B2"],
    )
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)
    
# ======================
# Detalhe por piloto
# ======================
with tab_pilotos:
    st.subheader("🏎️ Detalhe por Piloto")

    # Lista de pilotos com pelo menos 1 vitória (em toda a história)
    winners_all = df_completo[df_completo["position"] == "1"]
    winners_driver_ids = winners_all["driverId"].unique()
    driver_names_winners = driver_names[driver_names.index.isin(winners_driver_ids)]

    piloto_escolhido = st.selectbox(
        "Selecione um piloto", sorted(driver_names_winners.values)
    )

    if piloto_escolhido:
        driver_id = driver_names[driver_names == piloto_escolhido].index[0]

        # usa df_completo para evolução (não afetado pelo filtro de ano)
        winners_completo = df_completo[df_completo["position"] == "1"]
        pilot_wins = (
            winners_completo[winners_completo["driverId"] == driver_id]["year"]
            .value_counts()
            .sort_index()
        )

        pilot_wins_df = pilot_wins.reset_index()
        pilot_wins_df.columns = ["Ano", "Vitórias"]

        fig = px.line(
            pilot_wins_df,
            x="Ano",
            y="Vitórias",
            markers=True,
            title=f"Evolução de vitórias de {piloto_escolhido}",
        )
        st.plotly_chart(fig, use_container_width=True)



# ======================
# Vitórias por Equipe
# ======================
with tab_equipes:
    st.subheader("🏆 Títulos de Construtores (1958–presente)")
    # Pega a classificação final por ano e por construtor (última corrida do ano para cada construtor)
    cs_final = (
        cs_df.sort_values(["year", "raceId"])  # garante ordem dentro do ano
        .groupby(["year", "constructorId"], as_index=False)
        .tail(1)
    )
    # Garante que 'position' é numérico para comparar corretamente
    cs_final["position"] = pd.to_numeric(cs_final["position"], errors="coerce")
    # Campeão = posição 1 na classificação final daquele ano
    champs = cs_final[cs_final["position"] == 1]

    titles = champs["name"].value_counts().reset_index()
    titles.columns = ["Equipe", "Títulos"]

    fig = px.bar(
        titles,
        x="Equipe",
        y="Títulos",
        text="Títulos",
        color="Equipe",
        color_discrete_map=team_colors,
    )
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("🏆 Pontos dos Construtores no Ano")

    if selected_year != "Todos":
        cs_year = cs_df[cs_df["year"] == selected_year]
        # último standing por construtor no ano (total final de pontos)
        cs_last = cs_year.sort_values("raceId").groupby("constructorId", as_index=False).tail(1)

        pts = cs_last[["name", "points"]].sort_values("points", ascending=False)
        pts.rename(columns={"name": "Equipe", "points": "Pontos"}, inplace=True)

        fig = px.bar(
            pts,
            x="Equipe",
            y="Pontos",
            text="Pontos",
            color="Equipe",
            color_discrete_map=team_colors,  # usa o mesmo mapa de cores
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Selecione um ano na barra lateral para ver os pontos dos construtores.")
        
with tab_equipes:
    st.subheader("🏁 Vitórias por Equipe")

    constructor_names = constructors_df.set_index("constructorId")["name"]
    wins_by_teams = winners["constructorId"].map(constructor_names).value_counts()

    teams_df = wins_by_teams.reset_index()
    teams_df.columns = ["Equipe", "Vitórias"]

    # Mapa de cores oficiais por equipe (nomes conforme coluna 'name' de constructors.csv)

    fig = px.bar(
        teams_df.head(10),  # top 10
        x="Equipe",
        y="Vitórias",
        text="Vitórias",
        # Cores discretas por equipe
        color="Equipe",
        color_discrete_map=team_colors,
    )
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)
    
    
