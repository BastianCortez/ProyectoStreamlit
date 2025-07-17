import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from Utils.data_loader import load_perfume_data, get_accord_stats

# Configuración de página principal
st.set_page_config(
    page_title="Dashboard de Perfumes - Análisis Olfativo",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuración de página principal
st.set_page_config(
    page_title="Dashboard de Perfumes - Análisis Olfativo",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado para mejorar la apariencia
st.markdown("""
<style>
    .main-header {
        background: #2C3E50;
        padding: 3rem 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
        box-shadow: 0 4px 20px rgba(44, 62, 80, 0.3);
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 2.8rem;
        font-weight: 300;
        letter-spacing: 2px;
        color: white;
    }
    
    .main-header p {
        margin: 1rem 0 0 0;
        font-size: 1.1rem;
        opacity: 0.9;
        font-weight: 300;
    }
    
    .metric-card {
        background: white;
        padding: 2rem;
        border-radius: 8px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        border-top: 4px solid #34495E;
        margin: 1rem 0;
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.12);
    }
    
    .metric-card h4 {
        color: #2C3E50;
        margin: 0 0 1rem 0;
        font-size: 0.9rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .metric-card h2 {
        margin: 0.5rem 0;
        font-size: 2.2rem;
        font-weight: 700;
    }
    
    .metric-card p {
        color: #7F8C8D;
        margin: 0;
        font-size: 0.85rem;
        font-weight: 400;
    }
    
    .navigation-card {
        background: white;
        padding: 2.5rem;
        border-radius: 8px;
        box-shadow: 0 2px 15px rgba(0, 0, 0, 0.06);
        margin: 1.5rem 0;
        transition: all 0.3s ease;
        border: 1px solid #ECF0F1;
        min-height: 300px;
    }
    
    .navigation-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);
        border-color: #BDC3C7;
    }
    
    .navigation-card h3 {
        color: #2C3E50;
        margin: 0 0 1.5rem 0;
        font-size: 1.3rem;
        font-weight: 600;
        border-bottom: 2px solid #3498DB;
        padding-bottom: 0.8rem;
    }
    
    .navigation-card p {
        color: #34495E;
        line-height: 1.7;
        margin-bottom: 1.5rem;
        font-size: 0.95rem;
    }
    
    .navigation-card ul {
        color: #2C3E50;
        padding-left: 1.5rem;
        margin: 0;
    }
    
    .navigation-card li {
        margin: 0.5rem 0;
        color: #34495E;
        font-size: 0.9rem;
    }
    
    .chart-container {
        background: white;
        padding: 2rem;
        border-radius: 8px;
        box-shadow: 0 2px 15px rgba(0,0,0,0.06);
        margin: 2rem 0;
        border: 1px solid #ECF0F1;
    }
    
    .section-title {
        color: #2C3E50;
        font-size: 1.8rem;
        font-weight: 600;
        margin: 3rem 0 2rem 0;
        padding-bottom: 0.8rem;
        border-bottom: 2px solid #3498DB;
    }
    
    /* Mejorar métricas de Streamlit */
    [data-testid="metric-container"] {
        background: white;
        border: 1px solid #ECF0F1;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.06);
    }
</style>
""", unsafe_allow_html=True)

# Header principal
st.markdown("""
<div class="main-header">
    <h1>Dashboard de Análisis de Perfumes</h1>
    <p>Exploración Interactiva de 521 Fragancias y sus Acordes Aromáticos</p>
</div>
""", unsafe_allow_html=True)

# Cargar datos
@st.cache_data
def load_data():
    df_full = load_perfume_data()
    # Tomar solo los primeros 521 perfumes que tienen información completa
    return df_full.head(521)

df = load_data()

if df.empty:
    st.error("No se pudieron cargar los datos. Verifica que el archivo 'data/perfumes_ordenado.csv' existe.")
    st.stop()

# Sidebar con información general
st.sidebar.title("Información del Dataset")
st.sidebar.metric("Total de Perfumes", f"{len(df):,}")

# Calcular estadísticas rápidas
accord_columns = [col for col in df.columns if col.startswith('accords.')]
active_accords = sum(1 for col in accord_columns if df[col].sum() > 0)
st.sidebar.metric("Acordes Activos", f"{active_accords}/74")

avg_rating = df['calificationNumbers.ratingValue'].mean()
if not pd.isna(avg_rating):
    st.sidebar.metric("Rating Promedio", f"{avg_rating:.2f}/5.0")

# Navegación principal
st.markdown('<h2 class="section-title">Navegación del Dashboard</h2>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="navigation-card">
        <h3>Acordes y Composición</h3>
        <p>Analiza los acordes aromáticos más frecuentes e intensos. Incluye radar charts, 
        correlaciones entre acordes y distribuciones de intensidad.</p>
        <ul>
            <li><strong>Radar de acordes seleccionados</strong></li>
            <li><strong>Ranking de popularidad</strong></li>
            <li><strong>Heatmap de correlaciones</strong></li>
            <li><strong>Distribuciones de intensidad</strong></li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="navigation-card">
        <h3>Uso y Características</h3>
        <p>Explora patrones temporales de uso, características de durabilidad 
        y proyección de las fragancias.</p>
        <ul>
            <li><strong>Análisis por estaciones</strong></li>
            <li><strong>Uso diurno vs nocturno</strong></li>
            <li><strong>Matriz durabilidad-proyección</strong></li>
            <li><strong>Patrones de género</strong></li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="navigation-card">
        <h3>Ratings y Performance</h3>
        <p>Examina las calificaciones, popularidad y performance de los perfumes 
        en diferentes dimensiones.</p>
        <ul>
            <li><strong>Scatter plot rating vs reviews</strong></li>
            <li><strong>Distribuciones por género</strong></li>
            <li><strong>Análisis de sentimientos</strong></li>
            <li><strong>Relación calidad-precio</strong></li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="navigation-card">
        <h3>Explorador Comparativo</h3>
        <p>Herramientas avanzadas para comparar perfumes, encontrar similitudes 
        y explorar recomendaciones.</p>
        <ul>
            <li><strong>Comparador lado a lado</strong></li>
            <li><strong>Búsqueda por similitud</strong></li>
            <li><strong>Recomendaciones automáticas</strong></li>
            <li><strong>Explorador de pirámides olfativas</strong></li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# Insights principales del dataset
st.markdown("---")
st.markdown('<h2 class="section-title">Insights Principales del Dataset</h2>', unsafe_allow_html=True)

# Calcular insights
accord_stats = get_accord_stats(df)
top_accords = sorted(accord_stats.items(), key=lambda x: x[1]['frequency'], reverse=True)[:5]

insight_cols = st.columns(3)

with insight_cols[0]:
    most_frequent_accord = top_accords[0][0].replace('accords.', '').title()
    frequency_pct = top_accords[0][1]['perfume_percentage']
    st.markdown(f"""
    <div class="metric-card">
        <h4>Acorde Más Popular</h4>
        <h2 style="color: #2C3E50; margin: 0.5rem 0;">{most_frequent_accord}</h2>
        <p>Presente en {frequency_pct:.1f}% de perfumes</p>
    </div>
    """, unsafe_allow_html=True)

with insight_cols[1]:
    # Perfume con más reviews
    most_reviewed = df.loc[df['calificationNumbers.ratingCount'].idxmax()]
    review_count = most_reviewed['calificationNumbers.ratingCount']
    st.markdown(f"""
    <div class="metric-card">
        <h4>Más Reseñado</h4>
        <h2 style="color: #3498DB; margin: 0.5rem 0;">{review_count:.0f}</h2>
        <p>reseñas totales</p>
    </div>
    """, unsafe_allow_html=True)

with insight_cols[2]:
    # Rating más alto
    highest_rated = df['calificationNumbers.ratingValue'].max()
    st.markdown(f"""
    <div class="metric-card">
        <h4>Rating Máximo</h4>
        <h2 style="color: #E74C3C; margin: 0.5rem 0;">{highest_rated:.2f}</h2>
        <p>de 5.0 estrellas</p>
    </div>
    """, unsafe_allow_html=True)

# Gráfico de resumen en la página principal
st.markdown("---")
st.markdown('<h2 class="section-title">Vista General: Top 10 Acordes</h2>', unsafe_allow_html=True)

# Crear gráfico de barras de top acordes
top_10_data = []
for accord, stats in top_accords[:10]:
    top_10_data.append({
        'Acorde': accord.replace('accords.', '').title(),
        'Frecuencia': stats['frequency'],
        'Porcentaje': stats['perfume_percentage'],
        'Intensidad Promedio': stats['mean_intensity']
    })

top_10_df = pd.DataFrame(top_10_data)

# Crear gráfico con colores profesionales
colors = ['#2C3E50', '#34495E', '#3498DB', '#2980B9', '#1ABC9C', 
          '#16A085', '#27AE60', '#229954', '#F39C12', '#E67E22']

fig = go.Figure(data=go.Bar(
    x=top_10_df['Acorde'],
    y=top_10_df['Frecuencia'],
    marker_color=colors,
    opacity=0.8,
    text=[f"{p:.1f}%" for p in top_10_df['Porcentaje']],
    textposition='outside',
    textfont=dict(size=11, color='#2C3E50'),
    hovertemplate='<b>%{x}</b><br>' +
                  'Frecuencia: %{y} perfumes<br>' +
                  'Porcentaje: %{text}<br>' +
                  '<extra></extra>'
))

fig.update_layout(
    title=dict(
        text="Frecuencia de los 10 Acordes Más Populares",
        font=dict(size=18, color='#2C3E50', family='Arial'),
        x=0.5
    ),
    xaxis_title="Acordes",
    yaxis_title="Número de Perfumes",
    paper_bgcolor='white',
    plot_bgcolor='white',
    font=dict(color='#2C3E50', size=11),
    height=480,
    margin=dict(t=80, b=80, l=60, r=60),
    xaxis=dict(
        tickangle=45,
        gridcolor='#ECF0F1',
        linecolor='#BDC3C7',
        tickfont=dict(size=10)
    ),
    yaxis=dict(
        gridcolor='#ECF0F1',
        linecolor='#BDC3C7'
    )
)

# Envolver el gráfico en un contenedor
st.markdown('<div class="chart-container">', unsafe_allow_html=True)
st.plotly_chart(fig, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)
yaxis=dict(
        gridcolor='#ECF0F1',
        linecolor='#BDC3C7'
    )

# Envolver el gráfico en un contenedor
st.markdown('<div class="chart-container">', unsafe_allow_html=True)
st.plotly_chart(fig, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)
