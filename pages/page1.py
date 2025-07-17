import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from Utils.data_loader import cargar_datos
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
    df = cargar_datos()
    # Limpieza de datos para ratings
    df_clean = df.dropna(subset=['calificationNumbers.ratingValue']).copy()
    df_clean['rating_category'] = pd.cut(
        df_clean['calificationNumbers.ratingValue'],
        bins=[0, 2, 3, 4, 4.5, 5],
        labels=['Malo', 'Regular', 'Bueno', 'Muy Bueno', 'Excelente']
    )
    # Procesamiento de reviews
    df_clean['review_category'] = pd.cut(
        df_clean['calificationNumbers.ratingCount'],
        bins=[0, 10, 50, 200, 1000, float('inf')],
        labels=['Nuevo', 'Poco Conocido', 'Conocido', 'Popular', 'Muy Popular']
    )
    return df_clean

def create_rating_distribution():
    """Crea histograma de distribución de ratings"""
    df = load_and_process_data()
    fig = px.histogram(
        df,
        x='calificationNumbers.ratingValue',
        nbins=20,
        title='Distribución de Calificaciones de Perfumes',
        labels={'calificationNumbers.ratingValue': 'Calificación', 'count': 'Cantidad de Perfumes'},
        color_discrete_sequence=[RATING_PALETTE[2]]
    )
    # Añadir línea de promedio
    mean_rating = df['calificationNumbers.ratingValue'].mean()
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
    # Validar que las columnas existen
    required_cols = ['name', 'brand', 'calificationNumbers.ratingValue', 'calificationNumbers.ratingCount']
    for col in required_cols:
        if col not in df.columns:
            st.warning(f"La columna '{col}' no existe en el dataset. No se puede mostrar el gráfico de dispersión.")
            return None
    # Eliminar filas con valores nulos en las columnas requeridas
    df = df.dropna(subset=required_cols)
    if df.empty:
        st.warning("No hay datos suficientes para mostrar el gráfico de dispersión.")
        return None
    fig = px.scatter(
        df,
        x='calificationNumbers.ratingCount',
        y='calificationNumbers.ratingValue',
        size='calificationNumbers.ratingValue',
        hover_data=['name', 'brand'],
        title='Relación entre Popularidad y Calificación',
        labels={'calificationNumbers.ratingCount': 'Número de Reviews', 'calificationNumbers.ratingValue': 'Calificación'}
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
    # Si no tienes columna 'gender', puedes eliminar esta función o adaptarla a otra columna
    st.info("No hay columna 'gender' en el dataset para este gráfico.")
    return None

def create_performance_radar():
    """Crea radar chart de características de performance"""
    df = load_and_process_data()
    st.info("No hay datos de performance disponibles en el dataset para radar chart.")
    return None

def create_top_rated_perfumes():
    """Crea tabla de perfumes mejor calificados"""
    df = load_and_process_data()
    # Filtrar perfumes con al menos 10 reviews
    df_filtered = df[df['calificationNumbers.ratingCount'] >= 10]
    top_perfumes = df_filtered.nlargest(20, 'calificationNumbers.ratingValue')[['name', 'brand', 'calificationNumbers.ratingValue', 'calificationNumbers.ratingCount']]
    fig = go.Figure(data=[go.Table(
        header=dict(
            values=['Perfume', 'Marca', 'Calificación', 'Reviews'],
            fill_color=RATING_PALETTE[0],
            align='left',
            font=dict(color='white', size=12)
        ),
        cells=dict(
            values=[top_perfumes['name'],
                   top_perfumes['brand'],
                   top_perfumes['calificationNumbers.ratingValue'].round(2),
                   top_perfumes['calificationNumbers.ratingCount']],
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
    df['popularity_tier'] = pd.cut(
        df['calificationNumbers.ratingCount'],
        bins=[0, 10, 50, 200, float('inf')],
        labels=['Nicho', 'Emergente', 'Establecido', 'Mainstream']
    )
    rating_by_popularity = df.groupby('popularity_tier')['calificationNumbers.ratingValue'].agg(['mean', 'count']).reset_index()
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
    top_brands = df['brand'].value_counts().head(15).index if 'brand' in df.columns else []
    if len(top_brands) == 0:
        st.info("No hay columna 'brand' en el dataset para este gráfico.")
        return None
    df_brands = df[df['brand'].isin(top_brands)]
    brand_stats = df_brands.groupby('brand').agg({
        'calificationNumbers.ratingValue': ['mean', 'count'],
        'calificationNumbers.ratingCount': 'sum'
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
    # Aplicar filtros
    df_filtered = df[
        (df['calificationNumbers.ratingValue'] >= min_rating) &
        (df['calificationNumbers.ratingCount'] >= min_reviews)
    ]
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Perfumes Analizados", len(df_filtered))
    with col2:
        st.metric("Rating Promedio", f"{df_filtered['calificationNumbers.ratingValue'].mean():.2f}")
    with col3:
        st.metric("Total de Reviews", f"{df_filtered['calificationNumbers.ratingCount'].sum():,}")
    with col4:
        st.metric("Mejor Calificado", f"{df_filtered['calificationNumbers.ratingValue'].max():.2f}")
    
    st.markdown("---")
    
    # Fila 1: Distribución y Scatter Plot
    col1, col2 = st.columns(2)
    with col1:
        fig_dist = create_rating_distribution()
        if fig_dist:
            st.plotly_chart(fig_dist, use_container_width=True)
    with col2:
        fig_scatter = create_rating_vs_reviews_scatter()
        if fig_scatter:
            st.plotly_chart(fig_scatter, use_container_width=True)
    
    # Fila 3: Tendencias de Rating
    fig_trends = create_rating_trends()
    if fig_trends:
        st.plotly_chart(fig_trends, use_container_width=True)
    # Fila 4: Performance por Marca
    fig_brand = create_brand_performance()
    if fig_brand:
        st.plotly_chart(fig_brand, use_container_width=True)
    # Fila 5: Top Perfumes
    fig_top = create_top_rated_perfumes()
    if fig_top:
        st.plotly_chart(fig_top, use_container_width=True)
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
            <p>Rating promedio: {df_filtered['calificationNumbers.ratingValue'].mean():.2f}</p>
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