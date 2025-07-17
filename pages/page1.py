import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import seaborn as sns
import matplotlib.pyplot as plt

from Utils.data_loader import load_perfume_data
from Utils.plotting import create_custom_palette, download_plot_button

# Configuración de página
st.set_page_config(
    page_title="Acordes y Composición - Dashboard Perfumes",
    page_icon="🌸",
    layout="wide"
)

# Cargar datos
@st.cache_data
def load_data():
    try:
        df = load_perfume_data()
        return df.head(521)  # Solo primeros 521
    except ImportError:
        # Fallback: cargar directamente
        try:
            df = pd.read_csv('data/perfumes_ordenado.csv')
            # Limpieza básica
            accord_columns = [col for col in df.columns if col.startswith('accords.')]
            df[accord_columns] = df[accord_columns].fillna(0)
            return df.head(521)
        except Exception as e:
            st.error(f"Error al cargar datos: {e}")
            return pd.DataFrame()

def download_plot_button(fig, filename_prefix):
    """Función simple para descargar gráficos"""
    html_bytes = fig.to_html().encode()
    st.download_button(
        label="Descargar Gráfico",
        data=html_bytes,
        file_name=f"{filename_prefix}.html",
        mime="text/html",
        help="Descarga el gráfico como archivo HTML interactivo"
    )

df = load_data()

# PALETAS PROFESIONALES
PRIMARY_PALETTE = [
    '#2C3E50',  # Azul oscuro profesional
    '#34495E',  # Gris azulado
    '#3498DB',  # Azul claro
    '#2980B9',  # Azul medio
    '#1ABC9C',  # Verde agua
    '#16A085',  # Verde agua oscuro
    '#27AE60',  # Verde
    '#229954',  # Verde oscuro
    '#F39C12',  # Naranja
    '#E67E22'   # Naranja oscuro
]

# Paleta de correlaciones
CORRELATION_PALETTE = ['#E74C3C', '#EC7063', '#F8F9FA', '#82E0AA', '#27AE60']

def hex_to_rgba(hex_color, alpha=0.2):
    """Convierte color hex a formato rgba"""
    hex_color = hex_color.lstrip('#')
    return f'rgba({int(hex_color[0:2], 16)}, {int(hex_color[2:4], 16)}, {int(hex_color[4:6], 16)}, {alpha})'

# TÍTULO Y INTRODUCCIÓN
st.title("Análisis de Acordes y Composición")
st.markdown("""
Explora la complejidad aromática de **521 perfumes** a través de sus acordes más característicos.
Los acordes representan las familias olfativas que definen la personalidad de cada fragancia.
""")

# SIDEBAR - CONTROLES INTERACTIVOS
st.sidebar.header("Controles de Filtrado")

# Obtener lista de acordes
accord_columns = [col for col in df.columns if col.startswith('accords.')]
accord_names = [col.replace('accords.', '').title() for col in accord_columns]

# Widget 1: Selector múltiple de acordes
selected_accords = st.sidebar.multiselect(
    "Selecciona acordes para analizar:",
    options=accord_names,
    default=['Amaderado', 'Cítrico', 'Dulce', 'Aromático', 'Florales'][:5],
    help="Elige los acordes que deseas visualizar en detalle"
)

# Widget 2: Slider de intensidad mínima
min_intensity = st.sidebar.slider(
    "Intensidad mínima de acorde (%):",
    min_value=0,
    max_value=100,
    value=50,
    help="Filtra perfumes con acordes de al menos esta intensidad"
)

# Widget 3: Número de top acordes a mostrar
top_n = st.sidebar.selectbox(
    "Número de acordes principales:",
    options=[10, 15, 20, 25],
    index=1,
    help="Define cuántos acordes mostrar en los rankings"
)

# PROCESAMIENTO DE DATOS
accord_stats = {}
for col in accord_columns:
    values = df[col].dropna()
    non_zero_values = values[values > 0]
    
    if len(non_zero_values) > 0:
        accord_stats[col] = {
            'frequency': len(non_zero_values),
            'mean_intensity': non_zero_values.mean(),
            'max_intensity': non_zero_values.max(),
            'perfume_percentage': (len(non_zero_values) / len(df)) * 100
        }

# Top acordes por frecuencia
top_accords = sorted(accord_stats.items(), 
                    key=lambda x: x[1]['frequency'], 
                    reverse=True)[:top_n]

# LAYOUT PRINCIPAL
col1, col2 = st.columns([2, 1])

with col1:
    # VISUALIZACIÓN 1: RADAR CHART DE ACORDES SELECCIONADOS
    st.subheader("Perfil Aromático - Acordes Seleccionados")
    
    if selected_accords:
        # Preparar datos para radar
        selected_accord_cols = [f'accords.{acc.lower()}' for acc in selected_accords]
        radar_data = []
        
        for col in selected_accord_cols:
            if col in df.columns:
                values = df[col].dropna()
                non_zero = values[values > 0]
                if len(non_zero) > 0:
                    radar_data.append({
                        'acorde': col.replace('accords.', '').title(),
                        'frecuencia': len(non_zero),
                        'intensidad_promedio': non_zero.mean(),
                        'porcentaje_perfumes': (len(non_zero) / len(df)) * 100
                    })
        
        if radar_data:
            radar_df = pd.DataFrame(radar_data)
            
            # Crear radar chart
            fig_radar = go.Figure()
            
            # Normalizar valores para el radar (0-100)
            categories = radar_df['acorde'].tolist()
            frequencies_norm = (radar_df['frecuencia'] / radar_df['frecuencia'].max() * 100).tolist()
            intensities_norm = radar_df['intensidad_promedio'].tolist()
            
            # Traza de frecuencia
            fig_radar.add_trace(go.Scatterpolar(
                r=frequencies_norm,
                theta=categories,
                fill='toself',
                name='Frecuencia (normalizada)',
                line=dict(color=PRIMARY_PALETTE[0], width=3),
                fillcolor=hex_to_rgba(PRIMARY_PALETTE[0], 0.2)
            ))
            
            # Traza de intensidad promedio
            fig_radar.add_trace(go.Scatterpolar(
                r=intensities_norm,
                theta=categories,
                fill='toself',
                name='Intensidad Promedio (%)',
                line=dict(color=PRIMARY_PALETTE[2], width=3),
                fillcolor=hex_to_rgba(PRIMARY_PALETTE[2], 0.2)
            ))
            
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 100],
                        tickfont=dict(size=11, color='#2C3E50'),  
                        gridcolor='#ECF0F1',
                        linecolor='#BDC3C7'
                    ),
                    angularaxis=dict(
                        tickfont=dict(size=12, color='#2C3E50'),  
                        linecolor='#BDC3C7'
                    )
                ),
                showlegend=True,
                title=dict(
                    text="Comparación de Frecuencia vs Intensidad",
                    font=dict(size=14, color='#2C3E50'),
                    x=0.5
                ),
                height=400,
                paper_bgcolor='white',
                plot_bgcolor='white',
                font=dict(color='#2C3E50'),
                legend=dict(
                    bgcolor='rgba(255,255,255,0.9)',
                    bordercolor='#2C3E50',
                    borderwidth=1,
                    font=dict(color='#2C3E50')
                )
            )
            
            st.plotly_chart(fig_radar, use_container_width=True)
            download_plot_button(fig_radar, "radar_acordes")
        else:
            st.warning("No se encontraron datos para los acordes seleccionados.")
    else:
        st.info("Selecciona al menos un acorde en el panel lateral.")

with col2:
    # VISUALIZACIÓN 2: TOP ACORDES - RANKING
    st.subheader("Ranking de Acordes")
    
    # Preparar datos para ranking
    ranking_data = []
    for accord, stats in top_accords[:10]:  # Top 10 para esta visualización
        ranking_data.append({
            'Acorde': accord.replace('accords.', '').title(),
            'Perfumes': stats['frequency'],
            'Porcentaje': f"{stats['perfume_percentage']:.1f}%",
            'Intensidad': f"{stats['mean_intensity']:.1f}%"
        })
    
    ranking_df = pd.DataFrame(ranking_data)
    
    st.dataframe(
        ranking_df,
        use_container_width=True,
        hide_index=True
    )

# SEGUNDA FILA DE VISUALIZACIONES
st.markdown("---")

col3, col4 = st.columns([1, 1])

with col3:
    # VISUALIZACIÓN 3: DISTRIBUCIÓN DE INTENSIDADES
    st.subheader("Distribución de Intensidades")
    
    if selected_accords:
        # Crear subplots para histogramas
        fig_hist = make_subplots(
            rows=len(selected_accords),
            cols=1,
            subplot_titles=[acc.title() for acc in selected_accords],
            vertical_spacing=0.1
        )
        
        for i, accord in enumerate(selected_accords):
            col_name = f'accords.{accord.lower()}'
            if col_name in df.columns:
                values = df[col_name].dropna()
                non_zero_values = values[values > 0]
                
                if len(non_zero_values) > 0:
                    # Calcular bins
                    bins = np.linspace(non_zero_values.min(), non_zero_values.max(), 15)
                    hist, bin_edges = np.histogram(non_zero_values, bins=bins)
                    
                    fig_hist.add_trace(
                        go.Bar(
                            x=bin_edges[:-1],
                            y=hist,
                            name=accord.title(),
                            marker_color=PRIMARY_PALETTE[i % len(PRIMARY_PALETTE)],
                            opacity=0.8,
                            showlegend=False
                        ),
                        row=i+1, col=1
                    )
        
        fig_hist.update_layout(
            height=180 * len(selected_accords),
            title=dict(
                text="Distribución de Intensidades por Acorde",
                font=dict(size=16, color='#2C3E50'),
                x=0.5
            ),
            showlegend=False,
            paper_bgcolor='white',
            plot_bgcolor='white',
            font=dict(color='#2C3E50')
        )
        
        fig_hist.update_xaxes(
            title_text="Intensidad (%)",
            gridcolor='#ECF0F1',
            linecolor='#BDC3C7',
            tickfont=dict(color='#2C3E50'),
            titlefont=dict(color='#2C3E50')
        )
        fig_hist.update_yaxes(
            title_text="Frecuencia",
            gridcolor='#ECF0F1',
            linecolor='#BDC3C7',
            tickfont=dict(color='#2C3E50'),
            titlefont=dict(color='#2C3E50')
        )
        
        st.plotly_chart(fig_hist, use_container_width=True)
        download_plot_button(fig_hist, "distribuciones_intensidad")

with col4:
    # VISUALIZACIÓN 4: HEATMAP DE CORRELACIONES
    st.subheader("Correlaciones entre Acordes")
    
    # Seleccionar top acordes para correlación
    top_accord_names = [acc[0] for acc in top_accords[:8]]  # Top 8 para visualización clara
    correlation_matrix = df[top_accord_names].corr()
    
    # Crear heatmap personalizado
    fig_corr = go.Figure(data=go.Heatmap(
        z=correlation_matrix.values,
        x=[col.replace('accords.', '').title() for col in correlation_matrix.columns],
        y=[col.replace('accords.', '').title() for col in correlation_matrix.index],
        colorscale=[
            [0, CORRELATION_PALETTE[0]],
            [0.25, CORRELATION_PALETTE[1]], 
            [0.5, CORRELATION_PALETTE[2]],
            [0.75, CORRELATION_PALETTE[3]],
            [1, CORRELATION_PALETTE[4]]
        ],
        zmid=0,
        colorbar=dict(
            title="Correlación",
            titlefont=dict(color='#2C3E50'),
            tickfont=dict(color='#2C3E50'),
            tickmode="linear",
            tick0=-1,
            dtick=0.5
        ),
        text=correlation_matrix.round(2).values,
        texttemplate="%{text}",
        textfont={"size": 11, "color": "#FFFFFF"},
        hoverongaps=False
    ))
    
    fig_corr.update_layout(
        title=dict(
            text="Correlaciones entre Acordes Principales",
            font=dict(size=14, color='#2C3E50')
        ),
        xaxis=dict(
            side="bottom", 
            tickangle=45,
            tickfont=dict(color='#2C3E50', size=10), 
            linecolor='#BDC3C7'
        ),
        yaxis=dict(
            side="left",
            tickfont=dict(color='#2C3E50', size=10), 
            linecolor='#BDC3C7'
        ),
        height=400,
        paper_bgcolor='white',
        plot_bgcolor='white',
        font=dict(color='#2C3E50')
    )
    
    st.plotly_chart(fig_corr, use_container_width=True)
    download_plot_button(fig_corr, "correlaciones_acordes")

# INSIGHTS Y CONCLUSIONES
st.markdown("---")
st.subheader("Insights Clave")

insight_cols = st.columns(3)

with insight_cols[0]:
    most_frequent = top_accords[0]
    st.metric(
        "Acorde Más Frecuente",
        most_frequent[0].replace('accords.', '').title(),
        f"{most_frequent[1]['perfume_percentage']:.1f}% de perfumes"
    )

with insight_cols[1]:
    avg_intensity = np.mean([stats['mean_intensity'] for _, stats in top_accords[:5]])
    st.metric(
        "Intensidad Promedio (Top 5)",
        f"{avg_intensity:.1f}%",
        "Acordes principales"
    )

with insight_cols[2]:
    total_combinations = len([acc for acc in accord_columns if df[acc].sum() > 0])
    st.metric(
        "Acordes Activos",
        f"{total_combinations}",
        "De 74 posibles"
    )

# Información técnica
with st.expander("Información Técnica"):
    st.markdown("""
    **Metodología de Análisis:**
    - **Acordes**: Intensidades expresadas como porcentajes (0-100%)
    - **Frecuencia**: Número de perfumes que contienen cada acorde
    - **Correlaciones**: Coeficiente de Pearson entre intensidades de acordes
    - **Filtros**: Aplicados dinámicamente según selección del usuario
    - **Dataset**: 521 perfumes con información completa
    
    **Paleta de Colores**: Diseño profesional con alta legibilidad
    """)
