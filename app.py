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
        background: linear-gradient(90deg, #8B4513 0%, #D2B48C 50%, #FFB6C1 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #8B4513;
        margin: 1rem 0;
    }
    
    .insight-box {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 8px;
        border: 1px solid #e9ecef;
        margin: 1rem 0;
    }
    
    .navigation-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
        transition: transform 0.2s;
    }
    
    .navigation-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
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
st.markdown("## 🗺️ Navegación del Dashboard")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="navigation-card">
        <h3>🌸 Acordes y Composición</h3>
        <p>Analiza los acordes aromáticos más frecuentes e intensos. Incluye radar charts, 
        correlaciones entre acordes y distribuciones de intensidad.</p>
        <ul>
            <li>Radar de acordes seleccionados</li>
            <li>Ranking de popularidad</li>
            <li>Heatmap de correlaciones</li>
            <li>Distribuciones de intensidad</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="navigation-card">
        <h3>⏰ Uso y Características</h3>
        <p>Explora patrones temporales de uso, características de durabilidad 
        y proyección de las fragancias.</p>
        <ul>
            <li>Análisis por estaciones</li>
            <li>Uso diurno vs nocturno</li>
            <li>Matriz durabilidad-proyección</li>
            <li>Patrones de género</li>
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
            <li>Scatter plot rating vs reviews</li>
            <li>Distribuciones por género</li>
            <li>Análisis de sentimientos</li>
            <li>Relación calidad-precio</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="navigation-card">
        <h3>🔍 Explorador Comparativo</h3>
        <p>Herramientas avanzadas para comparar perfumes, encontrar similitudes 
        y explorar recomendaciones.</p>
        <ul>
            <li>Comparador lado a lado</li>
            <li>Búsqueda por similitud</li>
            <li>Recomendaciones automáticas</li>
            <li>Explorador de pirámides olfativas</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# Insights principales del dataset
st.markdown("---")
st.markdown("## 🧠 Insights Principales del Dataset")

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
        <h2 style="color: #8B4513;">{most_frequent_accord}</h2>
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
        <h2 style="color: #D2B48C;">{review_count:.0f}</h2>
        <p>reseñas</p>
    </div>
    """, unsafe_allow_html=True)

with insight_cols[2]:
    # Complejidad promedio (número de acordes por perfume)
    accord_counts = (df[accord_columns] > 0).sum(axis=1)
    avg_complexity = accord_counts.mean()
    st.markdown(f"""
    <div class="metric-card">
        <h4>Complejidad Promedio</h4>
        <h2 style="color: #FFB6C1;">{avg_complexity:.1f}</h2>
        <p>acordes por perfume</p>
    </div>
    """, unsafe_allow_html=True)

with insight_cols[3]:
    # Rating más alto
    highest_rated = df['calificationNumbers.ratingValue'].max()
    st.markdown(f"""
    <div class="metric-card">
        <h4>Rating Máximo</h4>
        <h2 style="color: #FF8C00;">{highest_rated:.2f}</h2>
        <p>de 5.0 estrellas</p>
    </div>
    """, unsafe_allow_html=True)

# Gráfico de resumen en la página principal
st.markdown("---")
st.markdown("## 📈 Vista General: Top 10 Acordes")

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
    text=top_10_df['Porcentaje'].round(1),
    texttemplate='%{text}%',
    textposition='outside'
))

fig.update_layout(
    title="Frecuencia de los 10 Acordes Más Populares",
    xaxis_title="Acordes",
    yaxis_title="Número de Perfumes",
    paper_bgcolor='white',
    plot_bgcolor='white',
    font=dict(color='#2C3E50'),
    height=500
)

fig.update_xaxes(tickangle=45)

st.plotly_chart(fig, use_container_width=True)

# Información adicional
st.markdown("---")
st.markdown("## ℹ️ Información Técnica")

with st.expander("Detalles del Dataset y Metodología"):
    st.markdown("""
    ### Estructura del Dataset
    - **Total de registros**: 3,196 perfumes únicos
    - **Columnas**: 114 variables diferentes
    - **Acordes analizados**: 74 familias olfativas distintas
    
    ### Metodología de Análisis
    - **Acordes**: Medidos como porcentajes de intensidad (0-100%)
    - **Ratings**: Escala de 1.0 a 5.0 estrellas
    - **Frecuencia**: Número de perfumes que contienen cada acorde
    - **Correlaciones**: Coeficiente de Pearson entre intensidades
    
    ### Navegación del Dashboard
    Utiliza el menú lateral para navegar entre las diferentes páginas de análisis.
    Cada página ofrece herramientas interactivas específicas para explorar
    diferentes aspectos de los datos de perfumería.
    
    ### Interactividad
    - Filtros dinámicos en tiempo real
    - Descargas de gráficos y datos
    - Tooltips informativos
    - Múltiples vistas de los mismos datos
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem;">
    <p>Dashboard desarrollado para análisis académico de perfumería</p>
    <p>Datos procesados: 3,196 perfumes | 74 acordes aromáticos | Múltiples dimensiones de análisis</p>
</div>
""", unsafe_allow_html=True)