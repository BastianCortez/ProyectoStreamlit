# Dashboard de Análisis de Perfumes

Dashboard interactivo desarrollado en Streamlit para el análisis comprehensivo de 521 fragancias y sus características aromáticas. Esta aplicación proporciona visualizaciones profesionales y herramientas de exploración de datos para entender patrones en la industria de la perfumería.

## Características Principales

- **Dataset**: 521 perfumes con información completa
- **Acordes Aromáticos**: Análisis de 74 familias olfativas diferentes
- **Visualizaciones**: Múltiples tipos de gráficos interactivos con paletas personalizadas
- **Filtros Dinámicos**: Exploración de datos en tiempo real
- **Diseño Profesional**: Interfaz limpia y moderna sin elementos decorativos

## Instalación

### Prerrequisitos
- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Pasos de Instalación

1. **Clonar o descargar el proyecto**
   ```bash
   git clone [URL_DEL_REPOSITORIO]
   cd dashboard-perfumes
   ```

2. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

3. **Verificar estructura de archivos**
   ```
   dashboard-perfumes/
   ├── app.py
   ├── pages/
   │   ├── 01_Acordes_y_Composicion.py
   │   ├── 02_Calificaciones_y_Performance.py
   │   └── 03_Uso_y_Caracteristicas.py
   ├── Utils/
   │   ├── data_loader.py
   │   └── plotting.py
   ├── data/
   │   └── perfumes_ordenado.csv
   └── requirements.txt
   ```

4. **Ejecutar la aplicación**
   ```bash
   streamlit run app.py
   ```

5. **Acceder al dashboard**
   - La aplicación se abrirá automáticamente en el navegador
   - URL local: `http://localhost:8501`

## Estructura del Dashboard

### Página Principal (app.py)
**Vista General del Dataset**

Presenta una introducción al dashboard con métricas clave y navegación hacia las páginas especializadas. Incluye:

- Resumen estadístico del dataset (521 perfumes analizados)
- Gráfico de barras de los 5 acordes más populares
- Tarjetas de navegación hacia páginas específicas
- Métricas principales: acorde más frecuente, perfume más reseñado, rating máximo

### Acordes y Composición
**Análisis Profundo de Familias Olfativas**

Exploración detallada de los acordes aromáticos que definen cada fragancia:

- **Radar Chart**: Comparación de frecuencia vs intensidad de acordes seleccionados
- **Ranking Interactivo**: Tabla de top acordes con estadísticas de frecuencia
- **Distribuciones**: Histogramas de intensidad por acorde
- **Mapa de Correlaciones**: Heatmap mostrando relaciones entre acordes principales
- **Filtros**: Selección de acordes, intensidad mínima, número de acordes a mostrar

### Calificaciones y Performance
**Análisis de Popularidad y Evaluaciones**

Evaluación del rendimiento y recepción de los perfumes en el mercado:

- **Distribución de Ratings**: Histograma con líneas de promedio y mediana
- **Popularidad vs Calidad**: Scatter plot relacionando número de reviews con calificaciones
- **Análisis por Género**: Distribución de perfumes por categoría de género
- **Longevidad**: Análisis de votos por categorías de duración
- **Filtros**: Rating mínimo, número mínimo de reviews, géneros específicos

### Uso y Características
**Patrones Temporales y Características de Uso**

Análisis de cuándo y cómo se utilizan los perfumes:

- **Preferencias Estacionales**: Distribución de votos por estación del año
- **Uso Diurno vs Nocturno**: Comparación en gráfico de pastel
- **Análisis de Longevidad**: Distribución real de votos por categorías de duración
- **Proyección (Sillage)**: Análisis de intensidad de proyección
- **Radar por Género**: Preferencias estacionales según tipo de perfume
- **Mapa de Calor**: Visualización innovadora de preferencias género-estación


## Datos del Dataset

- **Total de perfumes**: 521 (con información completa)
- **Acordes analizados**: 74 familias olfativas
- **Variables**: 114 columnas incluyendo ratings, características temporales, género, precio
- **Fuente**: Datos procesados de plataformas especializadas en perfumería

## Tecnologías Utilizadas

- **Streamlit**: Framework principal para la aplicación web
- **Plotly**: Biblioteca de visualización interactiva
- **Pandas**: Manipulación y análisis de datos
- **NumPy**: Cálculos numéricos


## Soporte

Para reportar problemas o sugerir mejoras:
1. Verificar que todas las dependencias estén instaladas correctamente
2. Asegurar que el archivo `perfumes_ordenado.csv` esté en la carpeta `data/`
3. Comprobar que la estructura de directorios coincida con la especificada

## Licencia

Proyecto desarrollado para fines académicos y de análisis de datos.
