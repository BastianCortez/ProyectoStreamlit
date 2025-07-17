import streamlit as st
import pandas as pd
import plotly.express as px


@st.cache_data
def cargar_datos():
    df = pd.read_csv("data/perfumes_ordenado.csv")

    # Limpieza básica
    df.dropna(how='all', inplace=True)
    df.drop_duplicates(inplace=True)
    df.columns = df.columns.str.strip()  # eliminar espacios en los nombres

    return df
