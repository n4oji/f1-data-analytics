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

    return results, drivers, constructors, races


@st.cache_data
def load_constructor_standings():
    cs = pd.read_csv("data/constructor_standings.csv")
    races = pd.read_csv("data/races.csv")[["raceId", "year"]]
    constructors = pd.read_csv("data/constructors.csv")[["constructorId", "name"]]
    cs = cs.merge(races, on="raceId", how="left").merge(constructors, on="constructorId", how="left")
    return cs

@st.cache_data
def load_qualifying():
    return pd.read_csv("data/qualifying.csv")

@st.cache_data
def load_circuits():
    return pd.read_csv("data/circuits.csv")

def get_driver_names(drivers_df):
    return drivers_df.set_index("driverId").apply(
        lambda x: f"{x['forename']} {x['surname']}", axis=1
    )

def time_to_seconds(t):
    """Converte tempo do formato 'M:SS.xxx' para segundos (float)."""
    if pd.isna(t):
        return None
    try:
        parts = t.split(":")
        if len(parts) == 2:
            minutes, sec = parts
            return int(minutes) * 60 + float(sec)
        return float(parts[0])  
    except:
        return None

def seconds_to_minutes(segundos):
    minutos = int(segundos // 60)
    resto = segundos % 60
    return f"{minutos}:{resto:06.3f}"



# ======================
# App Streamlit
# ======================

st.set_page_config(page_title="Formula 1 Data Analytics", layout="wide")
st.title("Formula 1 Data Analytics 1950-2024")

# Carregar dados
df, pilots_df, constructors_df, races = load_data()
cs_df = load_constructor_standings()
qualifying_df = load_qualifying()
circuits = load_circuits()

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
tab_pilotos, tab_equipes, tab_circuitos = st.tabs(["Pilotos", "Equipes/Construtores", "Circuitos"])

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
    
 ## ======================
# Circuitos - Recordes e Estatísticas
# ======================
with tab_circuitos:
    st.subheader("🏟️ Estatísticas dos Circuitos")

    # Filtros
    circuitos_disponiveis = sorted(races["name"].unique())
    circuito_escolhido = st.selectbox("Selecione um circuito", ["Todos"] + circuitos_disponiveis)

    # Filtro principal para races pelo ano
    if selected_year != "Todos":
        races_filtrado = races[races["year"] == selected_year]
        df_filtrado_ano = df_completo[df_completo["year"] == selected_year]
        qualifying_filtrado_ano = qualifying_df[qualifying_df["raceId"].isin(races_filtrado["raceId"])]
    else:
        races_filtrado = races.copy()
        df_filtrado_ano = df_completo.copy()
        qualifying_filtrado_ano = qualifying_df.copy()

    # Filtro por circuito
    if circuito_escolhido != "Todos":
        race_ids_filtrados = races_filtrado[races_filtrado["name"] == circuito_escolhido]["raceId"]
        circuit_ids_escolhidos = races_filtrado[races_filtrado["name"] == circuito_escolhido]["circuitId"].unique()
        circuits_exibir = circuits[circuits["circuitId"].isin(circuit_ids_escolhidos)]
        df_circuito = df_filtrado_ano[df_filtrado_ano["raceId"].isin(race_ids_filtrados)]
        qual_df_circuito = qualifying_filtrado_ano[qualifying_filtrado_ano["raceId"].isin(race_ids_filtrados)]
        races_circuito = races_filtrado[races_filtrado["raceId"].isin(race_ids_filtrados)]
    else:
        circuits_exibir = circuits[circuits["circuitId"].isin(races_filtrado["circuitId"].unique())]
        df_circuito = df_filtrado_ano
        qual_df_circuito = qualifying_filtrado_ano
        races_circuito = races_filtrado

    if not qual_df_circuito.empty:
        qual_df_circuito = qual_df_circuito.merge(
            races[["raceId", "year", "name"]],
            on="raceId",
            how="left"
        )

    # Para destacar no mapa
    if circuito_escolhido != "Todos" and not circuits_exibir.empty:
        df_highlight = circuits_exibir
        df_others = circuits_exibir.iloc[0:0]
    else:
        df_highlight = pd.DataFrame()
        df_others = circuits_exibir

    # Zoom dinâmico do mapa
    zoom_lvl = 1
    map_center = None
    if len(circuits_exibir) == 1:
        lat_c = circuits_exibir.iloc[0]["lat"]
        lon_c = circuits_exibir.iloc[0]["lng"]
        map_center = {"lat": lat_c, "lon": lon_c}
        zoom_lvl = 6

    st.markdown("### 🗺️ Mapa dos Circuitos de F1")
    fig = px.scatter_mapbox(
        df_others,
        lat="lat",
        lon="lng",
        hover_name="name",
        hover_data={"location": True, "country": True},
        zoom=zoom_lvl,
        height=500,
        color_discrete_sequence=["#e63946"]
    )
    fig.update_traces(marker=dict(size=10), selector=dict(mode='markers'))

    if not df_highlight.empty:
        fig.add_trace(px.scatter_mapbox(
            df_highlight,
            lat="lat",
            lon="lng",
            hover_name="name",
            hover_data={"location": True, "country": True},
            color_discrete_sequence=["#FFD700"],
        ).data[0])
        fig.update_traces(marker=dict(size=18, color="#FFD700"), selector=1)

    fig.update_layout(
        mapbox_style="carto-darkmatter",
        margin={"r":0,"t":0,"l":0,"b":0},
        showlegend=False
    )
    if map_center:
        fig.update_layout(mapbox_center=map_center, mapbox_zoom=zoom_lvl)
    st.plotly_chart(fig, use_container_width=True)

    # =========================
    # Recordes de volta em corrida
    # =========================
    st.markdown("### ⏱️ Recorde de Volta em Corrida (Fastest Lap)")
    fastest_laps = df_circuito.dropna(subset=["fastestLapTime"])
    if not fastest_laps.empty:
        fastest_laps = fastest_laps.sort_values("fastestLapTime").groupby("name").first().reset_index()
        fastest_laps["Piloto"] = fastest_laps["driverId"].map(driver_names)
        fastest_laps = fastest_laps[["name", "year", "Piloto", "fastestLapTime"]]
        fastest_laps.columns = ["Circuito", "Ano", "Piloto", "Recorde Corrida"]
        st.dataframe(fastest_laps.style.highlight_min(subset=["Recorde Corrida"], color="#3A86FF", axis=0))
    else:
        st.write("Não há dados de voltas mais rápidas para este filtro.")

    # =========================
    # Recorde de classificação (Q3 mais rápido)
    # =========================
    st.markdown("### 🏁 Recorde de Classificação (Q3 mais rápido)")
    if not qual_df_circuito.empty:
        # Converte '\N' para None e calcula tempo em segundos
        for col in ["q1", "q2", "q3"]:
            qual_df_circuito[col] = qual_df_circuito[col].replace("\\N", None)
            qual_df_circuito[col] = qual_df_circuito[col].apply(time_to_seconds)

        # Só considera linhas onde Q3 está preenchido
        qual_df_q3 = qual_df_circuito[qual_df_circuito["q3"].notnull()].copy()
        if not qual_df_q3.empty:
            qual_best = qual_df_q3.sort_values("q3").groupby(["name", "year"]).first().reset_index()
            qual_best["Piloto"] = qual_best["driverId"].map(driver_names)
            qual_best = qual_best[["name", "year", "Piloto", "q3"]]
            qual_best.columns = ["Circuito", "Ano", "Piloto", "Recorde Classificação"]
            qual_best["Recorde Classificação"] = qual_best["Recorde Classificação"].apply(seconds_to_minutes)
            st.dataframe(qual_best.style.highlight_min(subset=["Recorde Classificação"], color="#3A86FF", axis=0))
        else:
            st.write("Não há tempos válidos de Q3 para este filtro.")
    else:
        st.write("Não há dados de classificação para este filtro.")

    # =========================
    # Evolução do recorde em volta
    # =========================
    st.markdown("### 📈 Evolução do Recorde de Volta no Circuito Selecionado")
    if circuito_escolhido != "Todos":
        laps_circuit = df_completo[df_completo["name"] == circuito_escolhido].dropna(subset=["fastestLapTime"])
        if not laps_circuit.empty:
            laps_circuit["fastestLapTime_s"] = laps_circuit["fastestLapTime"].apply(time_to_seconds)
            chart_df = laps_circuit.groupby("year")["fastestLapTime_s"].min().reset_index()
            fig_evol = px.line(chart_df, x="year", y="fastestLapTime_s", markers=True, title=f"Evolução do recorde de volta - {circuito_escolhido}")
            fig_evol.update_layout(xaxis_title="Ano", yaxis_title="Tempo (s)")
            st.plotly_chart(fig_evol, use_container_width=True)
        else:
            st.write("Não há evolução de recorde de volta para este circuito.")

    # =========================
    # Ranking de circuitos com mais GPs realizados
    # =========================
    st.markdown("### 🏟️ Circuitos com mais GPs realizados")
    gp_counts = races["name"].value_counts().head(10)
    st.bar_chart(gp_counts)

    # =========================
    # Ranking de circuitos com mais vencedores diferentes
    # =========================
    st.markdown("### 🏆 Circuitos com mais vencedores diferentes")
    winners_per_circuit = df_completo[df_completo["position"] == "1"].groupby("name")["driverId"].nunique()
    winners_per_circuit = winners_per_circuit.sort_values(ascending=False).head(10)
    st.bar_chart(winners_per_circuit)