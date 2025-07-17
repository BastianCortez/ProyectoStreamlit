import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from Utils.data_loader import load_perfume_data
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

SENTIMENT_PALETTE = [
    '#228B22',  # Verde bosque (Me Encanta)
    '#32CD32',  # Verde lima (Me Gusta)
    '#FFD700',  # Dorado (Indiferente)
    '#FF6347',  # Rojo tomate (No Me Gusta)
    '#8B0000',  # Rojo oscuro (La Odio)
]

@st.cache_data
def load_and_process_data():
    """Carga y procesa los datos para análisis de calificaciones"""
    df = load_perfume_data()
    
    # Renombrar columnas para facilitar el trabajo
    df = df.rename(columns={
        'calificationNumbers.ratingValue': 'rating',
        'calificationNumbers.ratingCount': 'ratingCount',
        'calificationNumbers.bestRating': 'bestRating'
    })
    
    # Limpieza de datos para ratings
    df_clean = df.dropna(subset=['rating']).copy()
    
    # Crear columna de género dominante
    gender_cols = ['gender.femenino', 'gender.masculino', 'gender.unisex', 
                   'gender.unisex_femenino', 'gender.unisex_masculino']
    df_clean['gender_dominant'] = df_clean[gender_cols].idxmax(axis=1).str.replace('gender.', '')
    
    # Crear categorías de rating
    df_clean['rating_category'] = pd.cut(df_clean['rating'], 
                                       bins=[0, 2, 3, 4, 4.5, 5], 
                                       labels=['Malo', 'Regular', 'Bueno', 'Muy Bueno', 'Excelente'])
    
    # Categorías de popularidad
    df_clean['popularity_category'] = pd.cut(df_clean['ratingCount'], 
                                           bins=[0, 10, 50, 200, 1000, float('inf')], 
                                           labels=['Nuevo', 'Poco Conocido', 'Conocido', 'Popular', 'Muy Popular'])
    
    # Calcular score de longevidad ponderado
    longevity_cols = ['longevity.escasa', 'longevity.débil', 'longevity.moderada', 'longevity.duradera', 'longevity.muy_duradera']
    longevity_weights = [1, 2, 3, 4, 5]
    df_clean['longevity_score'] = sum(df_clean[col] * weight for col, weight in zip(longevity_cols, longevity_weights))
    
    # Calcular score de sillage ponderado
    sillage_cols = ['sillage.suave', 'sillage.moderada', 'sillage.pesada', 'sillage.enorme']
    sillage_weights = [1, 2, 3, 4]
    df_clean['sillage_score'] = sum(df_clean[col] * weight for col, weight in zip(sillage_cols, sillage_weights))
    
    # Calcular score de precio ponderado
    price_cols = ['price.excelente_precio', 'price.buen_precio', 'price.precio_moderado', 'price.ligeramente_costoso', 'price.extremadamente_costoso']
    price_weights = [5, 4, 3, 2, 1]
    df_clean['value_score'] = sum(df_clean[col] * weight for col, weight in zip(price_cols, price_weights))
    
    return df_clean

def create_rating_distribution():
    """Crea histograma de distribución de ratings"""
    df = load_and_process_data()
    
    fig = px.histogram(
        df, 
        x='rating', 
        nbins=25,
        title='Distribución de Calificaciones de Perfumes',
        labels={'rating': 'Calificación', 'count': 'Cantidad de Perfumes'},
        color_discrete_sequence=[RATING_PALETTE[2]]
    )
    
    # Añadir líneas estadísticas
    mean_rating = df['rating'].mean()
    median_rating = df['rating'].median()
    
    fig.add_vline(x=mean_rating, line_dash="dash", line_color="red", 
                  annotation_text=f"Promedio: {mean_rating:.2f}")
    fig.add_vline(x=median_rating, line_dash="dot", line_color="blue", 
                  annotation_text=f"Mediana: {median_rating:.2f}")
    
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
        color='gender_dominant',
        size='rating',
        hover_data=['name'],
        title='Relación entre Popularidad y Calificación',
        labels={'ratingCount': 'Número de Reviews', 'rating': 'Calificación'},
        color_discrete_map=GENDER_PALETTE,
        log_x=True
    )
    
    fig.update_layout(
        height=500,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

def create_sentiment_analysis():
    """Crea análisis de sentimientos por rating"""
    df = load_and_process_data()
    
    sentiment_cols = ['calificationText.MeEncanta', 'calificationText.MeGusta', 
                     'calificationText.MeEsIndiferente', 'calificationText.NoMeGusta', 
                     'calificationText.LaOdio']
    
    # Calcular promedios por categoría de rating
    sentiment_by_rating = df.groupby('rating_category')[sentiment_cols].mean()
    sentiment_by_rating.columns = ['Me Encanta', 'Me Gusta', 'Indiferente', 'No Me Gusta', 'La Odio']
    
    fig = px.bar(
        sentiment_by_rating.reset_index(),
        x='rating_category',
        y=['Me Encanta', 'Me Gusta', 'Indiferente', 'No Me Gusta', 'La Odio'],
        title='Distribución de Sentimientos por Categoría de Rating',
        labels={'value': 'Proporción Promedio', 'rating_category': 'Categoría de Rating'},
        color_discrete_sequence=SENTIMENT_PALETTE
    )
    
    fig.update_layout(
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

def create_performance_radar():
    """Crea radar chart de características de performance por género"""
    df = load_and_process_data()
    
    performance_data = df.groupby('gender_dominant').agg({
        'longevity_score': 'mean',
        'sillage_score': 'mean',
        'rating': 'mean',
        'value_score': 'mean'
    }).round(2)
    
    fig = go.Figure()
    
    categories = ['Longevidad', 'Sillage', 'Rating', 'Relación Calidad-Precio']
    
    for i, gender in enumerate(performance_data.index):
        fig.add_trace(go.Scatterpolar(
            r=performance_data.loc[gender].values,
            theta=categories,
            fill='toself',
            name=gender.replace('_', ' ').title(),
            line_color=GENDER_PALETTE.get(gender, PERFORMANCE_PALETTE[i % len(PERFORMANCE_PALETTE)])
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, performance_data.values.max() * 1.1]
            )),
        showlegend=True,
        title="Performance Comparativo por Género",
        height=500
    )
    
    return fig

def create_longevity_sillage_analysis():
    """Crea análisis de longevidad vs sillage"""
    df = load_and_process_data()
    
    fig = px.scatter(
        df,
        x='longevity_score',
        y='sillage_score',
        color='rating',
        size='ratingCount',
        hover_data=['name', 'gender_dominant'],
        title='Análisis de Longevidad vs Sillage',
        labels={'longevity_score': 'Score de Longevidad', 'sillage_score': 'Score de Sillage'},
        color_continuous_scale='Viridis'
    )
    
    fig.update_layout(
        height=500,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

def create_seasonal_preferences():
    """Crea análisis de preferencias estacionales"""
    df = load_and_process_data()
    
    season_cols = ['timeSeasons.Invierno', 'timeSeasons.Primavera', 'timeSeasons.Verano', 'timeSeasons.Otoño']
    season_data = df[season_cols].mean()
    season_data.index = ['Invierno', 'Primavera', 'Verano', 'Otoño']
    
    fig = px.bar(
        x=season_data.index,
        y=season_data.values,
        title='Preferencias de Uso por Estación',
        labels={'x': 'Estación', 'y': 'Proporción Promedio de Uso'},
        color=season_data.values,
        color_continuous_scale='RdYlBu_r'
    )
    
    fig.update_layout(
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        showlegend=False
    )
    
    return fig

def create_price_vs_rating():
    """Crea análisis de precio vs rating"""
    df = load_and_process_data()
    
    fig = px.scatter(
        df,
        x='value_score',
        y='rating',
        color='gender_dominant',
        size='ratingCount',
        hover_data=['name'],
        title='Relación Calidad-Precio vs Rating',
        labels={'value_score': 'Score de Valor (mayor = mejor precio)', 'rating': 'Calificación'},
        color_discrete_map=GENDER_PALETTE
    )
    
    fig.update_layout(
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

def create_top_rated_table():
    """Crea tabla de perfumes mejor calificados"""
    df = load_and_process_data()
    
    # Filtrar perfumes con al menos 5 reviews para mayor confiabilidad
    df_filtered = df[df['ratingCount'] >= 5]
    top_perfumes = df_filtered.nlargest(15, 'rating')[['name', 'rating', 'ratingCount', 'gender_dominant', 'longevity_score', 'sillage_score']]
    
    fig = go.Figure(data=[go.Table(
        header=dict(
            values=['Perfume', 'Rating', 'Reviews', 'Género', 'Longevidad', 'Sillage'],
            fill_color=RATING_PALETTE[0],
            align='left',
            font=dict(color='white', size=12, family='Arial Black')
        ),
        cells=dict(
            values=[
                top_perfumes['name'], 
                top_perfumes['rating'].round(2),
                top_perfumes['ratingCount'].astype(int),
                top_perfumes['gender_dominant'].str.replace('_', ' ').str.title(),
                top_perfumes['longevity_score'].round(1),
                top_perfumes['sillage_score'].round(1)
            ],
            fill_color=[['white', 'lightgray'] * len(top_perfumes)],
            align='left',
            font=dict(color='black', size=11)
        )
    )])
    
    fig.update_layout(
        title="Top 15 Perfumes Mejor Calificados (mín. 5 reviews)",
        height=500
    )
    
    return fig

def create_gender_distribution():
    """Crea distribución de perfumes por género"""
    df = load_and_process_data()
    
    gender_counts = df['gender_dominant'].value_counts()
    gender_counts.index = gender_counts.index.str.replace('_', ' ').str.title()
    
    fig = px.pie(
        values=gender_counts.values,
        names=gender_counts.index,
        title='Distribución de Perfumes por Género',
        color_discrete_sequence=[GENDER_PALETTE.get(gender.lower().replace(' ', '_'), color) 
                               for gender, color in zip(gender_counts.index, RATING_PALETTE)]
    )
    
    fig.update_layout(height=400)
    
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
    min_reviews = st.sidebar.slider("Mínimo de Reviews", 0, int(df['ratingCount'].max()), 0)
    selected_genders = st.sidebar.multiselect(
        "Géneros a Analizar",
        df['gender_dominant'].unique(),
        default=df['gender_dominant'].unique()
    )
    
    # Filtros avanzados
    with st.sidebar.expander("Filtros Avanzados"):
        min_longevity = st.slider("Score Mínimo de Longevidad", 0.0, float(df['longevity_score'].max()), 0.0)
        min_sillage = st.slider("Score Mínimo de Sillage", 0.0, float(df['sillage_score'].max()), 0.0)
    
    # Aplicar filtros
    df_filtered = df[
        (df['rating'] >= min_rating) & 
        (df['ratingCount'] >= min_reviews) & 
        (df['gender_dominant'].isin(selected_genders)) &
        (df['longevity_score'] >= min_longevity) &
        (df['sillage_score'] >= min_sillage)
    ]
    
    # Métricas principales
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Perfumes Analizados", len(df_filtered))
    
    with col2:
        st.metric("Rating Promedio", f"{df_filtered['rating'].mean():.2f}")
    
    with col3:
        st.metric("Total Reviews", f"{df_filtered['ratingCount'].sum():,}")
    
    with col4:
        st.metric("Longevidad Promedio", f"{df_filtered['longevity_score'].mean():.1f}")
    
    with col5:
        st.metric("Sillage Promedio", f"{df_filtered['sillage_score'].mean():.1f}")
    
    st.markdown("---")
    
    # Fila 1: Distribución y Scatter Plot Principal
    col1, col2 = st.columns(2)
    
    with col1:
        st.plotly_chart(create_rating_distribution(), use_container_width=True)
    
    with col2:
        st.plotly_chart(create_rating_vs_reviews_scatter(), use_container_width=True)
    
    # Fila 2: Análisis de Sentimientos y Distribución por Género
    col1, col2 = st.columns(2)
    
    with col1:
        st.plotly_chart(create_sentiment_analysis(), use_container_width=True)
    
    with col2:
        st.plotly_chart(create_gender_distribution(), use_container_width=True)
    
    # Fila 3: Performance Radar y Longevidad vs Sillage
    col1, col2 = st.columns(2)
    
    with col1:
        st.plotly_chart(create_performance_radar(), use_container_width=True)
    
    with col2:
        st.plotly_chart(create_longevity_sillage_analysis(), use_container_width=True)
    
    # Fila 4: Análisis Estacional y Precio vs Rating
    col1, col2 = st.columns(2)
    
    with col1:
        st.plotly_chart(create_seasonal_preferences(), use_container_width=True)
    
    with col2:
        st.plotly_chart(create_price_vs_rating(), use_container_width=True)
    
    # Fila 5: Top Perfumes
    st.plotly_chart(create_top_rated_table(), use_container_width=True)
    
    # Insights automáticos
    st.markdown("---")
    st.subheader("💡 Insights Clave")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        best_gender = df_filtered.groupby('gender_dominant')['rating'].mean().idxmax()
        st.info(f"**Género mejor valorado:** {best_gender.replace('_', ' ').title()}")
    
    with col2:
        best_season = df_filtered[['timeSeasons.Invierno', 'timeSeasons.Primavera', 'timeSeasons.Verano', 'timeSeasons.Otoño']].mean().idxmax().replace('timeSeasons.', '')
        st.info(f"**Estación más popular:** {best_season}")
    
    with col3:
        correlation = df_filtered['rating'].corr(df_filtered['longevity_score'])
        st.info(f"**Correlación Rating-Longevidad:** {correlation:.2f}")
    
    # Botón de descarga
    st.markdown("---")
    if st.button("📊 Descargar Análisis Completo"):
        html_content = f"""
        <html>
        <head>
            <title>Análisis de Calificaciones - Dashboard de Perfumes</title>
            <style>
                body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 20px; background-color: #f8f9fa; }}
                .header {{ background: linear-gradient(135deg, #FFD700, #FF6B35); padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
                .chart {{ margin: 20px 0; padding: 15px; background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                h1 {{ color: white; text-align: center; margin: 0; }}
                .metrics {{ display: flex; justify-content: space-around; margin: 20px 0; }}
                .metric {{ text-align: center; background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📊 Análisis de Calificaciones y Performance</h1>
            </div>
            <div class="metrics">
                <div class="metric">
                    <h3>Perfumes Analizados</h3>
                    <p>{len(df_filtered):,}</p>
                </div>
                <div class="metric">
                    <h3>Rating Promedio</h3>
                    <p>{df_filtered['rating'].mean():.2f}</p>
                </div>
                <div class="metric">
                    <h3>Total Reviews</h3>
                    <p>{df_filtered['ratingCount'].sum():,}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        st.download_button(
            label="📥 Descargar Reporte HTML",
            data=html_content,
            file_name="analisis_calificaciones_completo.html",
            mime="text/html"
        )

if __name__ == "__main__":
    main()