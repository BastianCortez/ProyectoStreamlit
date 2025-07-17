import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from Utils.data_loader import load_perfume_data

st.set_page_config(
    page_title="Uso y Características",
    page_icon="⏰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# PALETAS PROFESIONALES
TEMPORAL_PALETTE = [
    '#2C3E50',  # Azul oscuro
    '#34495E',  # Gris azulado
    '#3498DB',  # Azul claro
    '#2980B9',  # Azul medio
    '#1ABC9C',  # Verde agua
]

SEASON_PALETTE = {
    'Invierno': '#2C3E50',     # Azul oscuro
    'Primavera': '#27AE60',    # Verde
    'Verano': '#F39C12',       # Naranja
    'Otoño': '#E74C3C'         # Rojo
}

GENDER_PALETTE = {
    'femenino': '#E74C3C',      # Rojo
    'masculino': '#3498DB',     # Azul
    'unisex': '#2ECC71',        # Verde
    'unisex_femenino': '#E67E22', # Naranja
    'unisex_masculino': '#9B59B6' # Púrpura
}

LONGEVITY_PALETTE = ['#E74C3C', '#E67E22', '#F39C12', '#27AE60', '#2ECC71']
SILLAGE_PALETTE = ['#3498DB', '#2980B9', '#8E44AD', '#9B59B6']

@st.cache_data
def load_and_process_data():
    """Carga y procesa los datos para análisis temporal"""
    df_full = load_perfume_data()
    df = df_full.head(521)  # Solo primeros 521
    
    # Renombrar columnas para facilitar el trabajo
    df = df.rename(columns={
        'calificationNumbers.ratingValue': 'rating',
        'calificationNumbers.ratingCount': 'ratingCount'
    })
    
    # Limpieza de datos
    df_clean = df.dropna(subset=['rating']).copy()
    
    # Crear columna de género dominante
    gender_cols = ['gender.femenino', 'gender.masculino', 'gender.unisex', 
                   'gender.unisex_femenino', 'gender.unisex_masculino']
    df_clean['gender_dominant'] = df_clean[gender_cols].idxmax(axis=1).str.replace('gender.', '')
    
    return df_clean

def create_seasonal_analysis(df_filtered):
    """Crea análisis de uso por estaciones"""
    season_cols = ['timeSeasons.Invierno', 'timeSeasons.Primavera', 'timeSeasons.Verano', 'timeSeasons.Otoño']
    season_labels = ['Invierno', 'Primavera', 'Verano', 'Otoño']
    
    # Sumar votos por estación
    season_votes = df_filtered[season_cols].sum()
    season_votes.index = season_labels
    
    fig = px.bar(
        x=season_votes.index,
        y=season_votes.values,
        title='Preferencias de Uso por Estación del Año',
        labels={'x': 'Estación', 'y': 'Total de Votos'},
        color=season_votes.index,
        color_discrete_map=SEASON_PALETTE
    )
    
    fig.update_layout(
        height=400,
        paper_bgcolor='white',
        plot_bgcolor='white',
        font=dict(color='#2C3E50'),
        title=dict(font=dict(color='#2C3E50', size=14)),
        xaxis=dict(
            gridcolor='#ECF0F1',
            linecolor='#BDC3C7',
            tickfont=dict(color='#2C3E50'),
            title=dict(font=dict(color='#2C3E50'))
        ),
        yaxis=dict(
            gridcolor='#ECF0F1',
            linecolor='#BDC3C7',
            tickfont=dict(color='#2C3E50'),
            title=dict(font=dict(color='#2C3E50'))
        ),
        showlegend=False
    )
    
    return fig

def create_day_night_analysis(df_filtered):
    """Crea análisis de uso diurno vs nocturno"""
    day_night_data = {
        'Día': df_filtered['timeDay.Dia'].sum(),
        'Noche': df_filtered['timeDay.Noche'].sum()
    }
    
    fig = px.pie(
        values=list(day_night_data.values()),
        names=list(day_night_data.keys()),
        title='Distribución de Uso: Día vs Noche',
        color_discrete_sequence=[TEMPORAL_PALETTE[2], TEMPORAL_PALETTE[0]]
    )
    
    fig.update_layout(
        height=400,
        paper_bgcolor='white',
        font=dict(color='#2C3E50'),
        title=dict(font=dict(color='#2C3E50', size=14)),
        legend=dict(
            bgcolor='rgba(255,255,255,0.9)',
            bordercolor='#ECF0F1',
            borderwidth=1,
            font=dict(color='#2C3E50')
        )
    )
    
    return fig

def create_longevity_analysis(df_filtered):
    """Crea análisis de longevidad"""
    longevity_cols = ['longevity.escasa', 'longevity.débil', 'longevity.moderada', 'longevity.duradera', 'longevity.muy_duradera']
    longevity_labels = ['Escasa', 'Débil', 'Moderada', 'Duradera', 'Muy Duradera']
    
    # Sumar votos por categoría
    longevity_votes = df_filtered[longevity_cols].sum()
    longevity_votes.index = longevity_labels
    
    fig = px.bar(
        x=longevity_votes.index,
        y=longevity_votes.values,
        title='Distribución de Votos por Longevidad',
        labels={'x': 'Categoría de Longevidad', 'y': 'Total de Votos'},
        color=longevity_votes.values,
        color_continuous_scale='Blues'
    )
    
    fig.update_layout(
        height=400,
        paper_bgcolor='white',
        plot_bgcolor='white',
        font=dict(color='#2C3E50'),
        title=dict(font=dict(color='#2C3E50', size=14)),
        xaxis=dict(
            gridcolor='#ECF0F1',
            linecolor='#BDC3C7',
            tickfont=dict(color='#2C3E50'),
            title=dict(font=dict(color='#2C3E50'))
        ),
        yaxis=dict(
            gridcolor='#ECF0F1',
            linecolor='#BDC3C7',
            tickfont=dict(color='#2C3E50'),
            title=dict(font=dict(color='#2C3E50'))
        ),
        showlegend=False,
        coloraxis_colorbar=dict(
            title=dict(font=dict(color='#2C3E50')),
            tickfont=dict(color='#2C3E50')
        )
    )
    
    return fig

def create_sillage_analysis(df_filtered):
    """Crea análisis de sillage (proyección)"""
    sillage_cols = ['sillage.suave', 'sillage.moderada', 'sillage.pesada', 'sillage.enorme']
    sillage_labels = ['Suave', 'Moderada', 'Pesada', 'Enorme']
    
    # Sumar votos por categoría
    sillage_votes = df_filtered[sillage_cols].sum()
    sillage_votes.index = sillage_labels
    
    fig = px.bar(
        x=sillage_votes.index,
        y=sillage_votes.values,
        title='Distribución de Votos por Sillage (Proyección)',
        labels={'x': 'Categoría de Sillage', 'y': 'Total de Votos'},
        color=sillage_votes.values,
        color_continuous_scale='Purples'
    )
    
    fig.update_layout(
        height=400,
        paper_bgcolor='white',
        plot_bgcolor='white',
        font=dict(color='#2C3E50'),
        title=dict(font=dict(color='#2C3E50', size=14)),
        xaxis=dict(
            gridcolor='#ECF0F1',
            linecolor='#BDC3C7',
            tickfont=dict(color='#2C3E50'),
            title=dict(font=dict(color='#2C3E50'))
        ),
        yaxis=dict(
            gridcolor='#ECF0F1',
            linecolor='#BDC3C7',
            tickfont=dict(color='#2C3E50'),
            title=dict(font=dict(color='#2C3E50'))
        ),
        showlegend=False,
        coloraxis_colorbar=dict(
            title=dict(font=dict(color='#2C3E50')),
            tickfont=dict(color='#2C3E50')
        )
    )
    
    return fig

def create_gender_temporal_analysis(df_filtered):
    """Crea análisis temporal por género"""
    season_cols = ['timeSeasons.Invierno', 'timeSeasons.Primavera', 'timeSeasons.Verano', 'timeSeasons.Otoño']
    season_labels = ['Invierno', 'Primavera', 'Verano', 'Otoño']
    
    # Agrupar por género y calcular promedios por estación
    gender_season = df_filtered.groupby('gender_dominant')[season_cols].mean()
    gender_season.columns = season_labels
    
    fig = go.Figure()
    
    for gender in gender_season.index:
        fig.add_trace(go.Scatterpolar(
            r=gender_season.loc[gender].values,
            theta=season_labels,
            fill='toself',
            name=gender.replace('_', ' ').title(),
            line=dict(color=GENDER_PALETTE.get(gender, TEMPORAL_PALETTE[0]), width=2)
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, gender_season.values.max() * 1.1],
                tickfont=dict(color='#2C3E50'),
                gridcolor='#ECF0F1',
                linecolor='#BDC3C7'
            ),
            angularaxis=dict(
                tickfont=dict(color='#2C3E50'),
                linecolor='#BDC3C7'
            )
        ),
        showlegend=True,
        title=dict(
            text="Preferencias Estacionales por Género",
            font=dict(color='#2C3E50', size=14)
        ),
        height=500,
        paper_bgcolor='white',
        plot_bgcolor='white',
        font=dict(color='#2C3E50'),
        legend=dict(
            bgcolor='rgba(255,255,255,0.9)',
            bordercolor='#ECF0F1',
            borderwidth=1,
            font=dict(color='#2C3E50')
        )
    )
    
    return fig

def create_season_gender_heatmap(df_filtered):
    """Crea heatmap de estaciones vs género"""
    season_cols = ['timeSeasons.Invierno', 'timeSeasons.Primavera', 'timeSeasons.Verano', 'timeSeasons.Otoño']
    season_labels = ['Invierno', 'Primavera', 'Verano', 'Otoño']
    
    # Crear matriz género x estación (promedios)
    heatmap_data = df_filtered.groupby('gender_dominant')[season_cols].mean()
    heatmap_data.columns = season_labels
    
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data.values,
        x=season_labels,
        y=[g.replace('_', ' ').title() for g in heatmap_data.index],
        colorscale='RdYlBu',
        colorbar=dict(
            title=dict(
                text="Intensidad de Preferencia",
                font=dict(color='#2C3E50')
            ),
            tickfont=dict(color='#2C3E50')
        ),
        text=heatmap_data.round(2).values,
        texttemplate="%{text}",
        textfont={"size": 12, "color": "#FFFFFF"},
        hoverongaps=False
    ))
    
    fig.update_layout(
        title=dict(
            text="Mapa de Calor: Preferencias Estacionales por Género",
            font=dict(color='#2C3E50', size=14)
        ),
        xaxis=dict(
            title="Estaciones",
            tickfont=dict(color='#2C3E50'),
            title_font=dict(color='#2C3E50')
        ),
        yaxis=dict(
            title="Género",
            tickfont=dict(color='#2C3E50'),
            title_font=dict(color='#2C3E50')
        ),
        height=400,
        paper_bgcolor='white',
        plot_bgcolor='white',
        font=dict(color='#2C3E50')
    )
    
    return fig

# Interfaz principal
def main():
    st.title("Análisis de Uso y Características")
    st.markdown("---")
    
    # Sidebar con filtros
    st.sidebar.header("Filtros de Análisis")
    
    df = load_and_process_data()
    
    # Filtros
    min_rating = st.sidebar.slider("Rating Mínimo", 0.0, 5.0, 0.0, 0.1)
    min_reviews = st.sidebar.slider("Mínimo de Reviews", 0, int(df['ratingCount'].max()), 0)
    selected_genders = st.sidebar.multiselect(
        "Géneros a Analizar",
        df['gender_dominant'].unique(),
        default=df['gender_dominant'].unique()
    )
    
    # Aplicar filtros
    df_filtered = df[
        (df['rating'] >= min_rating) & 
        (df['ratingCount'] >= min_reviews) & 
        (df['gender_dominant'].isin(selected_genders))
    ]
    
    # Verificar si hay datos filtrados
    if len(df_filtered) == 0:
        st.warning("No hay perfumes que cumplan con los filtros seleccionados. Intenta ajustar los criterios.")
        return
    
    # Métricas principales
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Perfumes Analizados", len(df_filtered))
    
    with col2:
        season_total = df_filtered[['timeSeasons.Invierno', 'timeSeasons.Primavera', 'timeSeasons.Verano', 'timeSeasons.Otoño']].sum().sum()
        st.metric("Total Votos Estacionales", f"{season_total:,}")
    
    with col3:
        day_night_total = df_filtered[['timeDay.Dia', 'timeDay.Noche']].sum().sum()
        st.metric("Total Votos Día/Noche", f"{day_night_total:,}")
    
    st.markdown("---")
    
    # Fila 1: Análisis Estacional y Día/Noche
    col1, col2 = st.columns(2)
    
    with col1:
        st.plotly_chart(create_seasonal_analysis(df_filtered), use_container_width=True)
    
    with col2:
        st.plotly_chart(create_day_night_analysis(df_filtered), use_container_width=True)
    
    # Fila 2: Longevidad y Sillage
    col1, col2 = st.columns(2)
    
    with col1:
        st.plotly_chart(create_longevity_analysis(df_filtered), use_container_width=True)
    
    with col2:
        st.plotly_chart(create_sillage_analysis(df_filtered), use_container_width=True)
    
    # Fila 3: Radar por Género y Heatmap Estacional
    col1, col2 = st.columns(2)
    
    with col1:
        st.plotly_chart(create_gender_temporal_analysis(df_filtered), use_container_width=True)
    
    with col2:
        st.plotly_chart(create_season_gender_heatmap(df_filtered), use_container_width=True)
    
    # Insights automáticos
    st.markdown("---")
    st.subheader("Insights Clave")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Estación más popular
        season_cols = ['timeSeasons.Invierno', 'timeSeasons.Primavera', 'timeSeasons.Verano', 'timeSeasons.Otoño']
        season_votes = df_filtered[season_cols].sum()
        most_popular_season = season_votes.idxmax().replace('timeSeasons.', '')
        st.info(f"**Estación más popular:** {most_popular_season}")
    
    with col2:
        # Momento del día preferido
        day_votes = df_filtered['timeDay.Dia'].sum()
        night_votes = df_filtered['timeDay.Noche'].sum()
        preferred_time = "Día" if day_votes > night_votes else "Noche"
        st.info(f"**Momento preferido:** {preferred_time}")
    
    with col3:
        # Longevidad más común
        longevity_cols = ['longevity.escasa', 'longevity.débil', 'longevity.moderada', 'longevity.duradera', 'longevity.muy_duradera']
        longevity_votes = df_filtered[longevity_cols].sum()
        most_common_longevity = longevity_votes.idxmax().replace('longevity.', '').title()
        st.info(f"**Longevidad más votada:** {most_common_longevity}")

if __name__ == "__main__":
    main()
