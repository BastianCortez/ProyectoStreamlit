import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from Utils.data_loader import load_data
from Utils.plotting import RATING_PALETTE, PERFORMANCE_PALETTE, GENDER_PALETTE
import plotly.io as pio

# Configuración de la página
st.set_page_config(
    page_title="Calificaciones y Performance",
    page_icon="⭐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Paletas de colores personalizadas para esta página
RATING_PALETTE = [
    '#FFD700',  # Dorado (excelente)
    '#FF6B35',  # Naranja rojizo (muy bueno)
    '#F7931E',  # Naranja (bueno)
    '#FFB84D',  # Naranja claro (regular)
    '#8B4513',  # Marrón (malo)
]

PERFORMANCE_PALETTE = [
    '#2E8B57',  # Verde bosque (longevidad)
    '#4682B4',  # Azul acero (proyección)
    '#9370DB',  # Violeta (durabilidad)
    '#DC143C',  # Rojo carmesí (intensidad)
    '#FF8C00',  # Naranja oscuro (calidad)
]

GENDER_PALETTE = {
    'femenino': '#FF69B4',      # Rosa intenso
    'masculino': '#4169E1',     # Azul real
    'unisex': '#32CD32',        # Verde lima
    'unisex_femenino': '#FF1493', # Rosa profundo
    'unisex_masculino': '#1E90FF' # Azul dodger
}

@st.cache_data
def load_and_process_data():
    """Carga y procesa los datos para análisis de calificaciones"""
    df = load_data()
    
    # Limpieza de datos para ratings
    df_clean = df.dropna(subset=['rating']).copy()
    df_clean['rating_category'] = pd.cut(df_clean['rating'], 
                                       bins=[0, 2, 3, 4, 4.5, 5], 
                                       labels=['Malo', 'Regular', 'Bueno', 'Muy Bueno', 'Excelente'])
    
    # Procesamiento de reviews
    df_clean['review_category'] = pd.cut(df_clean['ratingCount'], 
                                       bins=[0, 10, 50, 200, 1000, float('inf')], 
                                       labels=['Nuevo', 'Poco Conocido', 'Conocido', 'Popular', 'Muy Popular'])
    
    return df_clean

def create_rating_distribution():
    """Crea histograma de distribución de ratings"""
    df = load_and_process_data()
    
    fig = px.histogram(
        df, 
        x='rating', 
        nbins=20,
        title='Distribución de Calificaciones de Perfumes',
        labels={'rating': 'Calificación', 'count': 'Cantidad de Perfumes'},
        color_discrete_sequence=[RATING_PALETTE[2]]
    )
    
    # Añadir línea de promedio
    mean_rating = df['rating'].mean()
    fig.add_vline(x=mean_rating, line_dash="dash", line_color="red", 
                  annotation_text=f"Promedio: {mean_rating:.2f}")
    
    fig.update_layout(
        showlegend=False,
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

def create_rating_vs_reviews_scatter():
    """Crea scatter plot de rating vs número de reviews"""
    df = load_and_process_data()
    
    fig = px.scatter(
        df,
        x='ratingCount',
        y='rating',
        color='gender',
        size='rating',
        hover_data=['name', 'brand'],
        title='Relación entre Popularidad y Calificación',
        labels={'ratingCount': 'Número de Reviews', 'rating': 'Calificación'},
        color_discrete_map=GENDER_PALETTE
    )
    
    fig.update_layout(
        height=500,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

def create_rating_by_gender_boxplot():
    """Crea box plot de ratings por género"""
    df = load_and_process_data()
    
    fig = px.box(
        df,
        x='gender',
        y='rating',
        title='Distribución de Calificaciones por Género',
        labels={'gender': 'Género', 'rating': 'Calificación'},
        color='gender',
        color_discrete_map=GENDER_PALETTE
    )
    
    fig.update_layout(
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

def create_performance_radar():
    """Crea radar chart de características de performance"""
    df = load_and_process_data()
    
    # Calcular promedios por género
    performance_cols = ['longevity', 'sillage', 'projection']
    available_cols = [col for col in performance_cols if col in df.columns]
    
    if not available_cols:
        st.warning("No hay datos de performance disponibles en el dataset")
        return None
    
    gender_performance = df.groupby('gender')[available_cols].mean()
    
    fig = go.Figure()
    
    for i, gender in enumerate(gender_performance.index):
        fig.add_trace(go.Scatterpolar(
            r=gender_performance.loc[gender].values,
            theta=available_cols,
            fill='toself',
            name=gender.title(),
            line_color=GENDER_PALETTE.get(gender, PERFORMANCE_PALETTE[i])
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 5]
            )),
        showlegend=True,
        title="Performance Promedio por Género",
        height=500
    )
    
    return fig

def create_top_rated_perfumes():
    """Crea tabla de perfumes mejor calificados"""
    df = load_and_process_data()
    
    # Filtrar perfumes con al menos 10 reviews
    df_filtered = df[df['ratingCount'] >= 10]
    top_perfumes = df_filtered.nlargest(20, 'rating')[['name', 'brand', 'rating', 'ratingCount', 'gender']]
    
    fig = go.Figure(data=[go.Table(
        header=dict(
            values=['Perfume', 'Marca', 'Calificación', 'Reviews', 'Género'],
            fill_color=RATING_PALETTE[0],
            align='left',
            font=dict(color='white', size=12)
        ),
        cells=dict(
            values=[top_perfumes['name'], 
                   top_perfumes['brand'],
                   top_perfumes['rating'].round(2),
                   top_perfumes['ratingCount'],
                   top_perfumes['gender']],
            fill_color='lavender',
            align='left',
            font=dict(color='black', size=11)
        )
    )])
    
    fig.update_layout(
        title="Top 20 Perfumes Mejor Calificados (mín. 10 reviews)",
        height=600
    )
    
    return fig

def create_rating_trends():
    """Crea análisis de tendencias de rating"""
    df = load_and_process_data()
    
    # Crear bins de popularidad
    df['popularity_tier'] = pd.cut(df['ratingCount'], 
                                 bins=[0, 10, 50, 200, float('inf')], 
                                 labels=['Nicho', 'Emergente', 'Establecido', 'Mainstream'])
    
    rating_by_popularity = df.groupby('popularity_tier')['rating'].agg(['mean', 'count']).reset_index()
    
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Rating Promedio por Popularidad', 'Cantidad de Perfumes por Categoría'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # Gráfico de barras para rating promedio
    fig.add_trace(
        go.Bar(
            x=rating_by_popularity['popularity_tier'],
            y=rating_by_popularity['mean'],
            name='Rating Promedio',
            marker_color=RATING_PALETTE[1]
        ),
        row=1, col=1
    )
    
    # Gráfico de barras para cantidad
    fig.add_trace(
        go.Bar(
            x=rating_by_popularity['popularity_tier'],
            y=rating_by_popularity['count'],
            name='Cantidad',
            marker_color=RATING_PALETTE[3]
        ),
        row=1, col=2
    )
    
    fig.update_layout(
        height=400,
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

def create_brand_performance():
    """Crea análisis de performance por marca"""
    df = load_and_process_data()
    
    # Top 15 marcas por cantidad de perfumes
    top_brands = df['brand'].value_counts().head(15).index
    df_brands = df[df['brand'].isin(top_brands)]
    
    brand_stats = df_brands.groupby('brand').agg({
        'rating': ['mean', 'count'],
        'ratingCount': 'sum'
    }).round(2)
    
    brand_stats.columns = ['rating_promedio', 'cantidad_perfumes', 'total_reviews']
    brand_stats = brand_stats.sort_values('rating_promedio', ascending=True)
    
    fig = px.bar(
        brand_stats.reset_index(),
        x='rating_promedio',
        y='brand',
        orientation='h',
        title='Rating Promedio por Marca (Top 15)',
        labels={'rating_promedio': 'Rating Promedio', 'brand': 'Marca'},
        color='rating_promedio',
        color_continuous_scale=RATING_PALETTE
    )
    
    fig.update_layout(
        height=600,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

# Interfaz principal
def main():
    st.title("⭐ Análisis de Calificaciones y Performance")
    st.markdown("---")
    
    # Sidebar con filtros
    st.sidebar.header("Filtros de Análisis")
    
    df = load_and_process_data()
    
    # Filtros
    min_rating = st.sidebar.slider("Rating Mínimo", 0.0, 5.0, 0.0, 0.1)
    min_reviews = st.sidebar.slider("Mínimo de Reviews", 0, 1000, 0, 10)
    selected_genders = st.sidebar.multiselect(
        "Géneros a Analizar",
        df['gender'].unique(),
        default=df['gender'].unique()
    )
    
    # Aplicar filtros
    df_filtered = df[
        (df['rating'] >= min_rating) & 
        (df['ratingCount'] >= min_reviews) & 
        (df['gender'].isin(selected_genders))
    ]
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Perfumes Analizados", len(df_filtered))
    
    with col2:
        st.metric("Rating Promedio", f"{df_filtered['rating'].mean():.2f}")
    
    with col3:
        st.metric("Total de Reviews", f"{df_filtered['ratingCount'].sum():,}")
    
    with col4:
        st.metric("Mejor Calificado", f"{df_filtered['rating'].max():.2f}")
    
    st.markdown("---")
    
    # Fila 1: Distribución y Scatter Plot
    col1, col2 = st.columns(2)
    
    with col1:
        st.plotly_chart(create_rating_distribution(), use_container_width=True)
    
    with col2:
        st.plotly_chart(create_rating_vs_reviews_scatter(), use_container_width=True)
    
    # Fila 2: Box Plot y Radar Chart
    col1, col2 = st.columns(2)
    
    with col1:
        st.plotly_chart(create_rating_by_gender_boxplot(), use_container_width=True)
    
    with col2:
        radar_fig = create_performance_radar()
        if radar_fig:
            st.plotly_chart(radar_fig, use_container_width=True)
        else:
            st.info("Radar chart de performance no disponible - datos faltantes")
    
    # Fila 3: Tendencias de Rating
    st.plotly_chart(create_rating_trends(), use_container_width=True)
    
    # Fila 4: Performance por Marca
    st.plotly_chart(create_brand_performance(), use_container_width=True)
    
    # Fila 5: Top Perfumes
    st.plotly_chart(create_top_rated_perfumes(), use_container_width=True)
    
    # Botón de descarga
    st.markdown("---")
    if st.button("Descargar Análisis de Calificaciones"):
        # Crear HTML con todos los gráficos
        html_content = f"""
        <html>
        <head>
            <title>Análisis de Calificaciones - Dashboard de Perfumes</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .chart {{ margin: 20px 0; }}
                h1 {{ color: #8B4513; }}
            </style>
        </head>
        <body>
            <h1>Análisis de Calificaciones y Performance</h1>
            <p>Perfumes analizados: {len(df_filtered)}</p>
            <p>Rating promedio: {df_filtered['rating'].mean():.2f}</p>
            <div class="chart">{create_rating_distribution().to_html()}</div>
            <div class="chart">{create_rating_vs_reviews_scatter().to_html()}</div>
            <div class="chart">{create_rating_by_gender_boxplot().to_html()}</div>
            <div class="chart">{create_rating_trends().to_html()}</div>
            <div class="chart">{create_brand_performance().to_html()}</div>
            <div class="chart">{create_top_rated_perfumes().to_html()}</div>
        </body>
        </html>
        """
        
        st.download_button(
            label="Descargar Reporte HTML",
            data=html_content,
            file_name="analisis_calificaciones.html",
            mime="text/html"
        )

if __name__ == "__main__":
    main()