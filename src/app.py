import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from utils.flags import flags

# Load data
st.title('Formula 1 Data Analytics 🏎️')

# Adjust the path to where your F1 data file is actually located
df = pd.read_csv('data/results.csv')

winners = df[df['position'] == '1']
wins_by_drivers = winners['driverId'].value_counts().head(10)

pilots_df = pd.read_csv('data/drivers.csv')

# Create a mapping from driverId to full name
driver_names = pilots_df.set_index('driverId').apply(lambda x: f"{x['forename']} {x['surname']}", axis=1)

# Map driver IDs to names in the wins_by_drivers Series
wins_by_drivers.index = wins_by_drivers.index.map(driver_names)
wins_by_drivers.index.name = 'Piloto'
wins_by_drivers.name = 'Vitórias'

# Streamlit app
st.subheader('Top 10 Pilotos da F1 com mais vitórias')
st.write(wins_by_drivers)

# Plotar gráfico
fig, ax = plt.subplots(figsize=(8,5))
wins_by_drivers.plot(kind="bar", color="red", ax=ax)
ax.set_xlabel("Piloto")
ax.set_ylabel("Vitórias")
ax.set_title("Top 10 pilotos com mais vitórias")
ax.tick_params(axis='x', rotation=45)
plt.tight_layout()

st.pyplot(fig)


st.subheader('Nacionalidades dos pilotos e vitórias')
nationalities = pilots_df.set_index('driverId')['nationality']
wins_by_nationalities = winners['driverId'].map(nationalities).value_counts()
wins_by_nationalities.index = wins_by_nationalities.index.map(lambda x: f"{flags.get(x, '')} {x}")
wins_by_nationalities.index.name = 'Nacionalidade'
wins_by_nationalities.name = 'Vitórias'

st.write(wins_by_nationalities)

# Plotar gráfico
fig, ax = plt.subplots(figsize=(8,5))
wins_by_nationalities.plot(kind="bar", color="cyan", ax=ax)
ax.set_xlabel("Nacionalidade")
ax.set_ylabel("Vitórias")
ax.set_title("Vitórias por Nacionalidade")
ax.tick_params(axis='x', rotation=45)
plt.tight_layout()

st.pyplot(fig)
