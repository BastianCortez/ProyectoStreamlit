import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io

# Configuración de la página
st.set_page_config(
    page_title="Dashboard Interactivo",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Función para generar datos de ejemplo
@st.cache_data
def load_sample_data():
    """Genera datos de ejemplo para el dashboard"""
    np.random.seed(42)
    
    # Datos de ventas
    dates = pd.date_range(start='2023-01-01', end='2024-12-31', freq='D')
    sales_data = pd.DataFrame({
        'fecha': dates,
        'ventas': np.random.normal(1000, 200, len(dates)) + np.sin(np.arange(len(dates)) * 2 * np.pi / 365) * 100,
        'region': np.random.choice(['Norte', 'Sur', 'Centro', 'Oriente'], len(dates)),
        'producto': np.random.choice(['Producto A', 'Producto B', 'Producto C', 'Producto D'], len(dates)),
        'categoria': np.random.choice(['Electrónicos', 'Ropa', 'Hogar', 'Deportes'], len(dates))
    })
    
    # Datos de empleados
    employees_data = pd.DataFrame({
        'nombre': [f'Empleado {i}' for i in range(1, 101)],
        'departamento': np.random.choice(['Ventas', 'Marketing', 'IT', 'RRHH', 'Finanzas'], 100),
        'salario': np.random.normal(50000, 15000, 100),
        'experiencia': np.random.randint(1, 15, 100),
        'satisfaccion': np.random.randint(1, 11, 100),
        'edad': np.random.randint(22, 65, 100)
    })
    
    return sales_data, employees_data

# Función para descargar datos
def download_data(df, filename):
    """Permite descargar datos en formato CSV"""
    csv = df.to_csv(index=False)
    st.download_button(
        label="📥 Descargar CSV",
        data=csv,
        file_name=filename,
        mime="text/csv"
    )

# Función para crear visualizaciones con opción de descarga
def create_downloadable_plot(fig, filename):
    """Crea un plot con opción de descarga"""
    st.plotly_chart(fig, use_container_width=True)
    
    # Botón de descarga para la imagen
    img_bytes = fig.to_image(format="png")
    st.download_button(
        label="📥 Descargar Gráfico",
        data=img_bytes,
        file_name=filename,
        mime="image/png"
    )

def main():
    # Sidebar para navegación
    st.sidebar.title("🎯 Navegación")
    page = st.sidebar.selectbox(
        "Selecciona una página:",
        ["📊 Dashboard Principal", "💼 Análisis de Empleados", "📈 Análisis de Ventas"]
    )
    
    # Cargar datos
    sales_data, employees_data = load_sample_data()
    
    if page == "📊 Dashboard Principal":
        show_dashboard_principal(sales_data, employees_data)
    elif page == "💼 Análisis de Empleados":
        show_employee_analysis(employees_data)
    elif page == "📈 Análisis de Ventas":
        show_sales_analysis(sales_data)

def show_dashboard_principal(sales_data, employees_data):
    """Página principal del dashboard"""
    st.title("📊 Dashboard Principal")
    st.markdown("---")
    
    # Métricas generales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_sales = sales_data['ventas'].sum()
        st.metric("💰 Ventas Totales", f"${total_sales:,.0f}")
    
    with col2:
        avg_salary = employees_data['salario'].mean()
        st.metric("💼 Salario Promedio", f"${avg_salary:,.0f}")
    
    with col3:
        total_employees = len(employees_data)
        st.metric("👥 Total Empleados", total_employees)
    
    with col4:
        avg_satisfaction = employees_data['satisfaccion'].mean()
        st.metric("😊 Satisfacción Promedio", f"{avg_satisfaction:.1f}/10")
    
    st.markdown("---")
    
    # Gráfico de resumen - Scatter plot
    st.subheader("🔍 Análisis de Correlación: Experiencia vs Salario")
    
    # Widget interactivo - selectbox
    selected_dept = st.selectbox(
        "Selecciona un departamento:",
        ["Todos"] + list(employees_data['departamento'].unique())
    )
    
    # Filtrar datos según selección
    if selected_dept != "Todos":
        filtered_data = employees_data[employees_data['departamento'] == selected_dept]
    else:
        filtered_data = employees_data
    
    # Crear scatter plot
    fig_scatter = px.scatter(
        filtered_data,
        x='experiencia',
        y='salario',
        color='departamento',
        size='satisfaccion',
        hover_data=['nombre', 'edad'],
        title=f'Relación Experiencia-Salario {f"({selected_dept})" if selected_dept != "Todos" else ""}',
        labels={'experiencia': 'Años de Experiencia', 'salario': 'Salario (USD)'}
    )
    fig_scatter.update_layout(height=500)
    
    create_downloadable_plot(fig_scatter, "scatter_experiencia_salario.png")
    
    # Tabla con datos filtrados
    st.subheader("📋 Datos Detallados")
    st.dataframe(filtered_data.head(10))
    download_data(filtered_data, "empleados_filtrados.csv")

def show_employee_analysis(employees_data):
    """Página de análisis de empleados"""
    st.title("💼 Análisis de Empleados")
    st.markdown("---")
    
    # Widgets interactivos
    col1, col2 = st.columns(2)
    
    with col1:
        # Widget slider para filtrar por experiencia
        min_exp, max_exp = st.slider(
            "Rango de experiencia (años):",
            min_value=int(employees_data['experiencia'].min()),
            max_value=int(employees_data['experiencia'].max()),
            value=(1, 15)
        )
    
    with col2:
        # Widget multiselect para departamentos
        selected_depts = st.multiselect(
            "Selecciona departamentos:",
            employees_data['departamento'].unique(),
            default=employees_data['departamento'].unique()
        )
    
    # Filtrar datos
    filtered_employees = employees_data[
        (employees_data['experiencia'] >= min_exp) & 
        (employees_data['experiencia'] <= max_exp) &
        (employees_data['departamento'].isin(selected_depts))
    ]
    
    # Visualización 1: Histograma de salarios
    st.subheader("📊 Distribución de Salarios")
    fig_hist = px.histogram(
        filtered_employees,
        x='salario',
        nbins=20,
        color='departamento',
        title='Distribución de Salarios por Departamento',
        labels={'salario': 'Salario (USD)', 'count': 'Cantidad de Empleados'}
    )
    create_downloadable_plot(fig_hist, "histograma_salarios.png")
    
    # Visualización 2: Box plot de satisfacción
    st.subheader("📦 Niveles de Satisfacción por Departamento")
    fig_box = px.box(
        filtered_employees,
        x='departamento',
        y='satisfaccion',
        title='Distribución de Satisfacción Laboral',
        labels={'satisfaccion': 'Nivel de Satisfacción (1-10)', 'departamento': 'Departamento'}
    )
    create_downloadable_plot(fig_box, "boxplot_satisfaccion.png")
    
    # Tabla resumen
    st.subheader("📈 Estadísticas Resumidas")
    summary_stats = filtered_employees.groupby('departamento').agg({
        'salario': ['mean', 'median', 'std'],
        'experiencia': 'mean',
        'satisfaccion': 'mean',
        'edad': 'mean'
    }).round(2)
    
    st.dataframe(summary_stats)
    download_data(summary_stats, "estadisticas_empleados.csv")

def show_sales_analysis(sales_data):
    """Página de análisis de ventas"""
    st.title("📈 Análisis de Ventas")
    st.markdown("---")
    
    # Widgets interactivos
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Widget selectbox para región
        selected_region = st.selectbox(
            "Selecciona región:",
            ["Todas"] + list(sales_data['region'].unique())
        )
    
    with col2:
        # Widget multiselect para productos
        selected_products = st.multiselect(
            "Selecciona productos:",
            sales_data['producto'].unique(),
            default=sales_data['producto'].unique()
        )
    
    with col3:
        # Widget date input para rango de fechas
        date_range = st.date_input(
            "Rango de fechas:",
            value=(sales_data['fecha'].min(), sales_data['fecha'].max()),
            min_value=sales_data['fecha'].min(),
            max_value=sales_data['fecha'].max()
        )
    
    # Filtrar datos
    filtered_sales = sales_data[
        (sales_data['producto'].isin(selected_products)) &
        (sales_data['fecha'] >= pd.to_datetime(date_range[0])) &
        (sales_data['fecha'] <= pd.to_datetime(date_range[1]))
    ]
    
    if selected_region != "Todas":
        filtered_sales = filtered_sales[filtered_sales['region'] == selected_region]
    
    # Visualización 1: Gráfico de líneas temporal
    st.subheader("📊 Evolución de Ventas en el Tiempo")
    daily_sales = filtered_sales.groupby('fecha')['ventas'].sum().reset_index()
    
    fig_line = px.line(
        daily_sales,
        x='fecha',
        y='ventas',
        title='Evolución Diaria de Ventas',
        labels={'fecha': 'Fecha', 'ventas': 'Ventas (USD)'}
    )
    create_downloadable_plot(fig_line, "linea_ventas_tiempo.png")
    
    # Visualización 2: Gráfico de barras por categoría
    st.subheader("📊 Ventas por Categoría")
    category_sales = filtered_sales.groupby('categoria')['ventas'].sum().reset_index()
    
    fig_bar = px.bar(
        category_sales,
        x='categoria',
        y='ventas',
        title='Ventas Totales por Categoría',
        labels={'categoria': 'Categoría', 'ventas': 'Ventas (USD)'},
        color='ventas',
        color_continuous_scale='viridis'
    )
    create_downloadable_plot(fig_bar, "barras_ventas_categoria.png")
    
    # Visualización 3: Heatmap de ventas por región y producto
    st.subheader("🔥 Mapa de Calor: Ventas por Región y Producto")
    heatmap_data = filtered_sales.groupby(['region', 'producto'])['ventas'].sum().reset_index()
    heatmap_pivot = heatmap_data.pivot(index='region', columns='producto', values='ventas')
    
    fig_heatmap = px.imshow(
        heatmap_pivot,
        title='Ventas por Región y Producto',
        labels={'x': 'Producto', 'y': 'Región', 'color': 'Ventas (USD)'},
        color_continuous_scale='RdYlBu_r'
    )
    create_downloadable_plot(fig_heatmap, "heatmap_ventas.png")
    
    # Tabla de datos filtrados
    st.subheader("📋 Datos de Ventas Filtrados")
    st.dataframe(filtered_sales.head(20))
    download_data(filtered_sales, "ventas_filtradas.csv")

if __name__ == "__main__":
    main()