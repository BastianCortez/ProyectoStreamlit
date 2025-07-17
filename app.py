import streamlit as st
from pages import page1, page2, page3
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io
from Utils.data_loader import cargar_datos

# Configuración de la página
st.header("Visualización general del Dataset de Perfumes")

df = cargar_datos()

st.subheader("Vista previa del dataset")
st.dataframe(df, use_container_width=True)

st.subheader("Columnas disponibles")
st.write(df.columns.tolist())

st.subheader("Resumen estadístico")
st.write(df.describe(include="all"))

st.sidebar.header("Filtros")

nombres = st.sidebar.multiselect(
    "Selecciona uno o más perfumes",
    df["name"].unique(),
    default=df["name"].unique()
)

rating_min, rating_max = float(df["calificationNumbers.ratingValue"].min()), float(df["calificationNumbers.ratingValue"].max())
rango_rating = st.sidebar.slider("Rango de calificación", rating_min, rating_max, (rating_min, rating_max))

# Aplicar filtros solo con columnas existentes
df_filtrado = df[
    (df["name"].isin(nombres)) &
    (df["calificationNumbers.ratingValue"] >= rango_rating[0]) &
    (df["calificationNumbers.ratingValue"] <= rango_rating[1])
]

st.subheader("Tabla de perfumes filtrados")
st.dataframe(df_filtrado, use_container_width=True)

# ------------------ VISUALIZACIONES ------------------ #


# Visualización: cantidad de perfumes por calificación
st.subheader("Cantidad de perfumes por calificación")
conteo_rating = df_filtrado["calificationNumbers.ratingValue"].value_counts().reset_index()
conteo_rating.columns = ["Calificación", "Cantidad"]
fig1 = px.bar(conteo_rating, x="Calificación", y="Cantidad", color="Calificación", title="Perfumes por Calificación")
st.plotly_chart(fig1, use_container_width=True)

# Visualización: cantidad de perfumes por calificación
conteo_rating = df_filtrado["calificationNumbers.ratingValue"].value_counts().reset_index()
conteo_rating.columns = ["Calificación", "Cantidad"]
fig4 = px.bar(conteo_rating, x="Calificación", y="Cantidad", color="Calificación", title="Perfumes por Calificación")
st.plotly_chart(fig4, use_container_width=True)

# ------------------ DESCARGA ------------------ #

st.subheader("Descargar datos filtrados")
csv = df_filtrado.to_csv(index=False).encode('utf-8')
st.download_button("📥 Descargar CSV", csv, "perfumes_filtrados.csv", "text/csv")