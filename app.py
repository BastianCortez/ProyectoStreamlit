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

# CSS personalizado para mejorar la apariencia
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #8B4513 0%, #D2B48C 50%, #FFB6C1 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: bold;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .main-header p {
        margin: 0.5rem 0 0 0;
        font-size: 1.2rem;
        opacity: 0.9;
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        border-left: 5px solid #8B4513;
        margin: 1rem 0;
        transition: transform 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.15);
    }
    
    .metric-card h4 {
        color: #2C3E50;
        margin: 0 0 0.5rem 0;
        font-size: 1rem;
        font-weight: 600;
    }
    
    .metric-card h2 {
        margin: 0.5rem 0;
        font-size: 2rem;
        font-weight: bold;
    }
    
    .metric-card p {
        color: #7F8C8D;
        margin: 0;
        font-size: 0.9rem;
    }
    
    .navigation-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
        margin: 1.5rem 0;
        transition: all 0.3s ease;
        border: 1px solid #E8E8E8;
        height: auto;
        min-height: 280px;
    }
    
    .navigation-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        border-color: #8B4513;
    }
    
    .navigation-card h3 {
        color: #2C3E50;
        margin: 0 0 1rem 0;
        font-size: 1.4rem;
        font-weight: bold;
        border-bottom: 2px solid #8B4513;
        padding-bottom: 0.5rem;
    }
    
    .navigation-card p {
        color: #34495E;
        line-height: 1.6;
        margin-bottom: 1rem;
        font-size: 0.95rem;
    }
    
    .navigation-card ul {
        color: #2C3E50;
        padding-left: 1.2rem;
    }
    
    .navigation-card li {
        margin: 0.3rem 0;
        color: #34495E;
    }
    
    .insight-section {
        background: #F8F9FA;
        padding: 2rem;
        border-radius: 15px;
        margin: 2rem 0;
        border: 1px solid #E9ECEF;
    }
    
    .chart-container {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    
    /* Arreglar sidebar */
    .css-1d391kg {
        padding-top: 2rem;
    }
    
    /* Mejorar métricas de Streamlit */
    [data-testid="metric-container"] {
        background: white;
        border: 1px solid #E8E8E8;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    /* Títulos de sección */
    .section-title {
        color: #2C3E50;
        font-size: 1.8rem;
        font-weight: bold;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #8B4513;
    }
</style>
""", unsafe_allow_html=True)

# Header principal
st.markdown("""
<div class="main-header">
    <h1>🌸 Dashboard de Análisis de Perfumes</h1>
    <p>Exploración Interactiva de 3,196 Fragancias y sus Acordes Aromáticos</p>
</div>
""", unsafe_allow_html=True)

# Cargar datos
@st.cache_data
def load_data():
    return load_perfume_data()

df = load_data()

if df.empty:
    st.error("No se pudieron cargar los datos. Verifica que el archivo 'data/perfumes_ordenado.csv' existe.")
    st.stop()

# Sidebar con información general
st.sidebar.title("📊 Información del Dataset")
st.sidebar.metric("Total de Perfumes", f"{len(df):,}")

# Calcular estadísticas rápidas
accord_columns = [col for col in df.columns if col.startswith('accords.')]
active_accords = sum(1 for col in accord_columns if df[col].sum() > 0)
st.sidebar.metric("Acordes Activos", f"{active_accords}/74")

avg_rating = df['calificationNumbers.ratingValue'].mean()
if not pd.isna(avg_rating):
    st.sidebar.metric("Rating Promedio", f"{avg_rating:.2f}/5.0")

# Navegación principal
st.markdown('<h2 class="section-title">🗺️ Navegación del Dashboard</h2>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="navigation-card">
        <h3>🌸 Acordes y Composición</h3>
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
        <h3>⏰ Uso y Características</h3>
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
        <h3>⭐ Ratings y Performance</h3>
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
        <h3>🔍 Explorador Comparativo</h3>
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
st.markdown('<h2 class="section-title">🧠 Insights Principales del Dataset</h2>', unsafe_allow_html=True)

# Calcular insights
accord_stats = get_accord_stats(df)
top_accords = sorted(accord_stats.items(), key=lambda x: x[1]['frequency'], reverse=True)[:5]

insight_cols = st.columns(4)

with insight_cols[0]:
    most_frequent_accord = top_accords[0][0].replace('accords.', '').title()
    frequency_pct = top_accords[0][1]['perfume_percentage']
    st.markdown(f"""
    <div class="metric-card">
        <h4>Acorde Más Popular</h4>
        <h2 style="color: #8B4513; margin: 0.5rem 0;">{most_frequent_accord}</h2>
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
        <h2 style="color: #D2B48C; margin: 0.5rem 0;">{review_count:.0f}</h2>
        <p>reseñas totales</p>
    </div>
    """, unsafe_allow_html=True)

with insight_cols[2]:
    # Complejidad promedio (número de acordes por perfume)
    accord_counts = (df[accord_columns] > 0).sum(axis=1)
    avg_complexity = accord_counts.mean()
    st.markdown(f"""
    <div class="metric-card">
        <h4>Complejidad Promedio</h4>
        <h2 style="color: #FFB6C1; margin: 0.5rem 0;">{avg_complexity:.1f}</h2>
        <p>acordes por perfume</p>
    </div>
    """, unsafe_allow_html=True)

with insight_cols[3]:
    # Rating más alto
    highest_rated = df['calificationNumbers.ratingValue'].max()
    st.markdown(f"""
    <div class="metric-card">
        <h4>Rating Máximo</h4>
        <h2 style="color: #FF8C00; margin: 0.5rem 0;">{highest_rated:.2f}</h2>
        <p>de 5.0 estrellas</p>
    </div>
    """, unsafe_allow_html=True)

# Gráfico de resumen en la página principal
st.markdown("---")
st.markdown('<h2 class="section-title">📈 Vista General: Top 10 Acordes</h2>', unsafe_allow_html=True)

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

# Crear gráfico con colores personalizados
colors = ['#8B4513', '#D2B48C', '#FFB6C1', '#FF8C00', '#9ACD32', 
          '#DDA0DD', '#CD853F', '#FF69B4', '#20B2AA', '#F4A460']

fig = go.Figure(data=go.Bar(
    x=top_10_df['Acorde'],
    y=top_10_df['Frecuencia'],
    marker_color=colors,
    opacity=0.8,
    text=[f"{p:.1f}%" for p in top_10_df['Porcentaje']],
    textposition='outside',
    textfont=dict(size=12, color='#2C3E50'),
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
    font=dict(color='#2C3E50', size=12),
    height=500,
    margin=dict(t=80, b=60, l=60, r=60),
    xaxis=dict(
        tickangle=45,
        gridcolor='#E5E5E5',
        linecolor='#CCCCCC'
    ),
    yaxis=dict(
        gridcolor='#E5E5E5',
        linecolor='#CCCCCC'
    )
)

# Envolver el gráfico en un contenedor
st.markdown('<div class="chart-container">', unsafe_allow_html=True)
st.plotly_chart(fig, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# Información adicional
st.markdown("---")
st.markdown('<h2 class="section-title">ℹ️ Información Técnica</h2>', unsafe_allow_html=True)

with st.expander("📋 Detalles del Dataset y Metodología", expanded=False):
    col_info1, col_info2 = st.columns(2)
    
    with col_info1:
        st.markdown("""
        ### 📊 Estructura del Dataset
        - **Total de registros**: 3,196 perfumes únicos
        - **Columnas**: 114 variables diferentes  
        - **Acordes analizados**: 74 familias olfativas distintas
        - **Cobertura temporal**: Múltiples épocas de perfumería
        
        ### 🔬 Metodología de Análisis
        - **Acordes**: Medidos como porcentajes de intensidad (0-100%)
        - **Ratings**: Escala de 1.0 a 5.0 estrellas
        - **Frecuencia**: Número de perfumes que contienen cada acorde
        - **Correlaciones**: Coeficiente de Pearson entre intensidades
        """)
    
    with col_info2:
        st.markdown("""
        ### 🧭 Navegación del Dashboard
        Utiliza el **menú lateral** para navegar entre las diferentes páginas de análisis.
        Cada página ofrece herramientas interactivas específicas para explorar
        diferentes aspectos de los datos de perfumería.
        
        ### ⚡ Interactividad
        - **Filtros dinámicos** en tiempo real
        - **Descargas** de gráficos y datos
        - **Tooltips** informativos
        - **Múltiples vistas** de los mismos datos
        - **Visualizaciones responsivas**
        """)

# Footer mejorado
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #7F8C8D; padding: 2rem; background: #F8F9FA; border-radius: 10px; margin-top: 2rem;">
    <h4 style="color: #2C3E50; margin-bottom: 1rem;">Dashboard de Análisis de Perfumería</h4>
    <p style="margin: 0.5rem 0; font-size: 1rem;"><strong>Desarrollado para análisis académico avanzado</strong></p>
    <p style="margin: 0; font-size: 0.9rem;">
        📊 <strong>3,196 perfumes</strong> | 
        🌸 <strong>74 acordes aromáticos</strong> | 
        📈 <strong>Múltiples dimensiones de análisis</strong>
    </p>
    <p style="margin: 0.5rem 0 0 0; font-size: 0.8rem; opacity: 0.8;">
        Utiliza la navegación lateral para explorar las diferentes secciones del dashboard
    </p>
</div>
""", unsafe_allow_html=True)