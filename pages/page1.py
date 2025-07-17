import streamlit as st
from utils import cargar_datos
import plotly.express as px


st.header("Visualización general del Dataset de Perfumes")

df = cargar_datos()

st.subheader("Vista previa del dataset")
st.dataframe(df, use_container_width=True)

st.subheader("Columnas disponibles")
st.write(df.columns.tolist())

st.subheader("Resumen estadístico")
st.write(df.describe(include="all"))

st.sidebar.header("Filtros")

marcas = st.sidebar.multiselect("Selecciona una o más marcas", df["Marca"].unique(), default=df["Marca"].unique())
generos = st.sidebar.multiselect("Selecciona género", df["Género"].unique(), default=df["Género"].unique())
concentraciones = st.sidebar.multiselect("Concentración", df["Concentración"].unique(), default=df["Concentración"].unique())

precio_min, precio_max = int(df["Precio"].min()), int(df["Precio"].max())
rango_precio = st.sidebar.slider("Rango de precio", precio_min, precio_max, (precio_min, precio_max))

# Aplicar filtros
df_filtrado = df[
    (df["Marca"].isin(marcas)) &
    (df["Género"].isin(generos)) &
    (df["Concentración"].isin(concentraciones)) &
    (df["Precio"] >= rango_precio[0]) &
    (df["Precio"] <= rango_precio[1])
]

st.subheader("Tabla de perfumes filtrados")
st.dataframe(df_filtrado, use_container_width=True)

# ------------------ VISUALIZACIONES ------------------ #

st.subheader("Cantidad de perfumes por marca")
conteo_marcas = df_filtrado["Marca"].value_counts().reset_index()
conteo_marcas.columns = ["Marca", "Cantidad"]
fig1 = px.bar(conteo_marcas, x="Marca", y="Cantidad", color="Marca", title="Perfumes por Marca")
st.plotly_chart(fig1, use_container_width=True)

st.subheader("Precio promedio por marca")
precio_promedio = df_filtrado.groupby("Marca")["Precio"].mean().reset_index()
fig2 = px.line(precio_promedio, x="Marca", y="Precio", title="Precio promedio por Marca", markers=True)
st.plotly_chart(fig2, use_container_width=True)

st.subheader("Distribución de precios por género")
fig3 = px.box(df_filtrado, x="Género", y="Precio", color="Género", title="Distribución de precios por género")
st.plotly_chart(fig3, use_container_width=True)

# ------------------ DESCARGA ------------------ #

st.subheader("Descargar datos filtrados")
csv = df_filtrado.to_csv(index=False).encode('utf-8')
st.download_button("📥 Descargar CSV", csv, "perfumes_filtrados.csv", "text/csv")