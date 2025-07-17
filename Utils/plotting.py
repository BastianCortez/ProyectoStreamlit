import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from io import BytesIO
import base64

# PALETAS PERSONALIZADAS PARA EL DASHBOARD
PERFUME_PALETTES = {
    'primary': [
        '#8B4513',  # Marrón cálido (amaderado)
        '#D2B48C',  # Beige (atalcado) 
        '#FFB6C1',  # Rosa claro (dulce)
        '#FF8C00',  # Naranja (cítrico)
        '#9ACD32',  # Verde lima (aromático)
        '#DDA0DD',  # Ciruela (florales)
        '#CD853F',  # Marrón claro (cálido especiado)
        '#FF69B4',  # Rosa intenso (afrutados)
        '#20B2AA',  # Verde azulado (fresco especiado)
        '#F4A460'   # Arena (ámbar)
    ],
    
    'intensity': ['#FFF8DC', '#F0E68C', '#DAA520', '#B8860B', '#8B7355'],
    
    'correlation': ['#8B0000', '#FF6347', '#FFF8DC', '#98FB98', '#006400'],
    
    'gender': {
        'femenino': '#E91E63',
        'masculino': '#2196F3', 
        'unisex': '#9C27B0',
        'unisex_femenino': '#FF5722',
        'unisex_masculino': '#607D8B'
    },
    
    'seasons': {
        'primavera': '#4CAF50',
        'verano': '#FFC107', 
        'otoño': '#FF5722',
        'invierno': '#2196F3'
    },
    
    'rating': ['#F44336', '#FF5722', '#FF9800', '#4CAF50', '#2E7D32'],
    
    'price': ['#1B5E20', '#388E3C', '#66BB6A', '#A5D6A7', '#C8E6C9']
}

def create_custom_palette(palette_name, n_colors=None):
    """
    Crea una paleta personalizada
    """
    if palette_name in PERFUME_PALETTES:
        palette = PERFUME_PALETTES[palette_name]
        if isinstance(palette, list):
            if n_colors and n_colors <= len(palette):
                return palette[:n_colors]
            return palette
        return palette
    return PERFUME_PALETTES['primary']

def download_plot_button(fig, filename_prefix):
    """
    Crea un botón de descarga para gráficos plotly
    """
    # Convertir figura a HTML
    html_bytes = fig.to_html().encode()
    
    # Crear botón de descarga
    st.download_button(
        label="📥 Descargar Gráfico",
        data=html_bytes,
        file_name=f"{filename_prefix}.html",
        mime="text/html",
        help="Descarga el gráfico como archivo HTML interactivo"
    )

def create_radar_chart(data, categories, values, title="", colors=None):
    """
    Crea un gráfico de radar personalizado
    """
    if colors is None:
        colors = PERFUME_PALETTES['primary']
    
    fig = go.Figure()
    
    for i, (name, vals) in enumerate(zip(data.keys(), data.values())):
        fig.add_trace(go.Scatterpolar(
            r=vals,
            theta=categories,
            fill='toself',
            name=name,
            line=dict(color=colors[i % len(colors)], width=3),
            fillcolor=f'{colors[i % len(colors)]}33'
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, max(max(vals) for vals in data.values())],
                tickfont=dict(size=10),
                gridcolor='#E5E5E5'
            ),
            angularaxis=dict(
                tickfont=dict(size=12, color='#2C3E50')
            )
        ),
        showlegend=True,
        title=dict(
            text=title,
            font=dict(size=16, color='#2C3E50'),
            x=0.5
        ),
        paper_bgcolor='white',
        plot_bgcolor='white'
    )
    
    return fig

def create_correlation_heatmap(correlation_matrix, title=""):
    """
    Crea un heatmap de correlaciones personalizado
    """
    fig = go.Figure(data=go.Heatmap(
        z=correlation_matrix.values,
        x=[col.replace('accords.', '').title() for col in correlation_matrix.columns],
        y=[col.replace('accords.', '').title() for col in correlation_matrix.index],
        colorscale=[
            [0, PERFUME_PALETTES['correlation'][0]],
            [0.25, PERFUME_PALETTES['correlation'][1]], 
            [0.5, PERFUME_PALETTES['correlation'][2]],
            [0.75, PERFUME_PALETTES['correlation'][3]],
            [1, PERFUME_PALETTES['correlation'][4]]
        ],
        zmid=0,
        colorbar=dict(
            title="Correlación",
            titleside="right",
            tickmode="linear",
            tick0=-1,
            dtick=0.5
        ),
        text=correlation_matrix.round(2).values,
        texttemplate="%{text}",
        textfont={"size": 10},
        hoverongaps=False
    ))
    
    fig.update_layout(
        title=title,
        xaxis=dict(side="bottom", tickangle=45),
        yaxis=dict(side="left"),
        paper_bgcolor='white'
    )
    
    return fig

def create_bar_chart(data, x_col, y_col, title="", color_col=None, horizontal=False):
    """
    Crea gráfico de barras personalizado
    """
    colors = PERFUME_PALETTES['primary']
    
    if horizontal:
        fig = go.Figure(data=go.Bar(
            y=data[x_col],
            x=data[y_col],
            orientation='h',
            marker_color=colors[0],
            opacity=0.8
        ))
        fig.update_layout(
            xaxis_title=y_col,
            yaxis_title=x_col
        )
    else:
        fig = go.Figure(data=go.Bar(
            x=data[x_col],
            y=data[y_col],
            marker_color=colors[0],
            opacity=0.8
        ))
        fig.update_layout(
            xaxis_title=x_col,
            yaxis_title=y_col
        )
    
    fig.update_layout(
        title=title,
        paper_bgcolor='white',
        plot_bgcolor='white',
        font=dict(color='#2C3E50')
    )
    
    return fig

def create_scatter_plot(data, x_col, y_col, title="", size_col=None, color_col=None, hover_data=None):
    """
    Crea scatter plot personalizado
    """
    fig = go.Figure()
    
    # Determinar colores
    if color_col and color_col in data.columns:
        colors = data[color_col]
        colorscale = PERFUME_PALETTES['primary']
    else:
        colors = PERFUME_PALETTES['primary'][0]
    
    # Determinar tamaños
    if size_col and size_col in data.columns:
        sizes = data[size_col]
        # Normalizar tamaños
        sizes = (sizes - sizes.min()) / (sizes.max() - sizes.min()) * 20 + 5
    else:
        sizes = 8
    
    # Crear hover text
    hover_text = []
    if hover_data:
        for i, row in data.iterrows():
            text = "<br>".join([f"{col}: {row[col]}" for col in hover_data if col in data.columns])
            hover_text.append(text)
    else:
        hover_text = data.index
    
    fig.add_trace(go.Scatter(
        x=data[x_col],
        y=data[y_col],
        mode='markers',
        marker=dict(
            size=sizes,
            color=colors,
            colorscale=PERFUME_PALETTES['primary'] if color_col else None,
            opacity=0.7,
            line=dict(width=1, color='white')
        ),
        text=hover_text,
        hovertemplate='<b>%{text}</b><br>' + 
                     f'{x_col}: %{{x}}<br>' +
                     f'{y_col}: %{{y}}<extra></extra>'
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title=x_col,
        yaxis_title=y_col,
        paper_bgcolor='white',
        plot_bgcolor='white',
        font=dict(color='#2C3E50')
    )
    
    return fig

def create_histogram(data, column, title="", bins=20):
    """
    Crea histograma personalizado
    """
    fig = go.Figure(data=go.Histogram(
        x=data[column],
        nbinsx=bins,
        marker_color=PERFUME_PALETTES['primary'][0],
        opacity=0.8
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title=column,
        yaxis_title="Frecuencia",
        paper_bgcolor='white',
        plot_bgcolor='white',
        font=dict(color='#2C3E50')
    )
    
    return fig

def create_box_plot(data, category_col, value_col, title=""):
    """
    Crea box plot personalizado
    """
    categories = data[category_col].unique()
    colors = PERFUME_PALETTES['primary']
    
    fig = go.Figure()
    
    for i, category in enumerate(categories):
        category_data = data[data[category_col] == category][value_col]
        
        fig.add_trace(go.Box(
            y=category_data,
            name=str(category),
            marker_color=colors[i % len(colors)],
            opacity=0.8
        ))
    
    fig.update_layout(
        title=title,
        xaxis_title=category_col,
        yaxis_title=value_col,
        paper_bgcolor='white',
        plot_bgcolor='white',
        font=dict(color='#2C3E50')
    )
    
    return fig

def create_sunburst_chart(data, path_cols, value_col, title=""):
    """
    Crea gráfico sunburst personalizado
    """
    fig = go.Figure(go.Sunburst(
        labels=data[path_cols].values.flatten(),
        parents=[""] * len(data),
        values=data[value_col],
        branchvalues="total",
        marker=dict(
            colors=PERFUME_PALETTES['primary'][:len(data)]
        )
    ))
    
    fig.update_layout(
        title=title,
        paper_bgcolor='white',
        font=dict(color='#2C3E50')
    )
    
    return fig

def apply_custom_theme(fig):
    """
    Aplica tema personalizado consistente
    """
    fig.update_layout(
        paper_bgcolor='white',
        plot_bgcolor='white',
        font=dict(
            family="Arial, sans-serif",
            size=12,
            color='#2C3E50'
        ),
        title=dict(
            font=dict(size=16, color='#2C3E50'),
            x=0.5
        ),
        legend=dict(
            bgcolor='rgba(255,255,255,0.8)',
            bordercolor='#E5E5E5',
            borderwidth=1
        )
    )
    
    # Personalizar ejes
    fig.update_xaxes(
        gridcolor='#E5E5E5',
        linecolor='#CCCCCC',
        tickcolor='#CCCCCC'
    )
    
    fig.update_yaxes(
        gridcolor='#E5E5E5',
        linecolor='#CCCCCC',
        tickcolor='#CCCCCC'
    )
    
    return fig

def export_figure_data(fig, format='png'):
    """
    Exporta figura en diferentes formatos
    """
    if format == 'html':
        return fig.to_html()
    elif format == 'json':
        return fig.to_json()
    else:
        # Para PNG, SVG necesitaríamos kaleido
        return None

def create_metric_card(title, value, delta=None, delta_color="normal"):
    """
    Crea tarjeta de métrica personalizada
    """
    return {
        'title': title,
        'value': value,
        'delta': delta,
        'delta_color': delta_color
    }