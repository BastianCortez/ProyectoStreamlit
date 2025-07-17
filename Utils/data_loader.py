import pandas as pd
import streamlit as st
import numpy as np

@st.cache_data
def load_perfume_data():
    """
    Carga y procesa el dataset de perfumes
    Returns:
        pd.DataFrame: Dataset de perfumes limpio y procesado
    """
    try:
        # Cargar datos
        df = pd.read_csv('data/perfumes_ordenado.csv')
        
        # Limpieza básica
        df = df.copy()
        
        # Asegurar que las columnas numéricas sean float
        numeric_columns = [col for col in df.columns if any(prefix in col for prefix in [
            'accords.', 'calificationNumbers.', 'calificationText.', 
            'timeSeasons.', 'timeDay.', 'longevity.', 'sillage.', 
            'gender.', 'price.'
        ])]
        
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Rellenar NaN en acordes con 0 (significa que no tienen ese acorde)
        accord_columns = [col for col in df.columns if col.startswith('accords.')]
        df[accord_columns] = df[accord_columns].fillna(0)
        
        return df
        
    except Exception as e:
        st.error(f"Error al cargar los datos: {e}")
        return pd.DataFrame()

def get_accord_stats(df):
    """
    Calcula estadísticas de acordes
    """
    accord_columns = [col for col in df.columns if col.startswith('accords.')]
    stats = {}
    
    for col in accord_columns:
        values = df[col].dropna()
        non_zero_values = values[values > 0]
        
        if len(non_zero_values) > 0:
            stats[col] = {
                'frequency': len(non_zero_values),
                'mean_intensity': non_zero_values.mean(),
                'median_intensity': non_zero_values.median(),
                'max_intensity': non_zero_values.max(),
                'min_intensity': non_zero_values.min(),
                'std_intensity': non_zero_values.std(),
                'perfume_percentage': (len(non_zero_values) / len(df)) * 100
            }
    
    return stats

def filter_perfumes_by_accords(df, selected_accords, min_intensity=0):
    """
    Filtra perfumes basado en acordes seleccionados
    """
    if not selected_accords:
        return df
    
    # Convertir nombres de acordes a nombres de columnas
    accord_columns = [f'accords.{acc.lower()}' for acc in selected_accords]
    valid_columns = [col for col in accord_columns if col in df.columns]
    
    if not valid_columns:
        return df
    
    # Filtrar perfumes que tengan al menos uno de los acordes con intensidad mínima
    mask = (df[valid_columns] >= min_intensity).any(axis=1)
    
    return df[mask]

def get_perfume_profile(df, perfume_name):
    """
    Obtiene el perfil completo de un perfume específico
    """
    perfume = df[df['name'] == perfume_name]
    
    if perfume.empty:
        return None
    
    perfume = perfume.iloc[0]
    
    # Acordes del perfume
    accord_columns = [col for col in df.columns if col.startswith('accords.')]
    accords = {}
    
    for col in accord_columns:
        value = perfume[col]
        if pd.notna(value) and value > 0:
            accords[col.replace('accords.', '')] = value
    
    # Información básica
    profile = {
        'name': perfume['name'],
        'description': perfume.get('description', ''),
        'rating': perfume.get('calificationNumbers.ratingValue', None),
        'rating_count': perfume.get('calificationNumbers.ratingCount', None),
        'accords': dict(sorted(accords.items(), key=lambda x: x[1], reverse=True)),
        'pyramid': {
            'salida': perfume.get('piramidFragrance.salida', ''),
            'corazon': perfume.get('piramidFragrance.corazon', ''),
            'base': perfume.get('piramidFragrance.base', ''),
            'ingredientes': perfume.get('piramidFragrance.ingredientes', '')
        }
    }
    
    return profile

def get_similar_perfumes(df, perfume_name, top_n=5):
    """
    Encuentra perfumes similares basado en acordes
    """
    target_perfume = df[df['name'] == perfume_name]
    
    if target_perfume.empty:
        return []
    
    accord_columns = [col for col in df.columns if col.startswith('accords.')]
    target_accords = target_perfume[accord_columns].iloc[0]
    
    # Calcular similitud coseno
    similarities = []
    
    for idx, row in df.iterrows():
        if row['name'] == perfume_name:
            continue
            
        perfume_accords = row[accord_columns]
        
        # Similitud coseno
        dot_product = np.dot(target_accords, perfume_accords)
        norm_target = np.linalg.norm(target_accords)
        norm_perfume = np.linalg.norm(perfume_accords)
        
        if norm_target > 0 and norm_perfume > 0:
            similarity = dot_product / (norm_target * norm_perfume)
            similarities.append({
                'name': row['name'],
                'similarity': similarity,
                'rating': row.get('calificationNumbers.ratingValue', 0)
            })
    
    # Ordenar por similitud y retornar top N
    similarities.sort(key=lambda x: x['similarity'], reverse=True)
    return similarities[:top_n]

def export_filtered_data(df, format='csv'):
    """
    Exporta datos filtrados en diferentes formatos
    """
    if format == 'csv':
        return df.to_csv(index=False).encode('utf-8')
    elif format == 'json':
        return df.to_json(orient='records').encode('utf-8')
    else:
        return None