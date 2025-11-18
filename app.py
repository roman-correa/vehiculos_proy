import pandas as pd
import plotly.express as px
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np # Importar numpy para mejor manejo de nulos

# --- Configuración Inicial de la Página ---
st.set_page_config(
    page_title="Dashboard de Vehículos en Venta",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Título Principal ---
st.header('🚗 **VEHÍCULOS EN VENTA**')
st.markdown("Explora el mercado de vehículos filtrando por marca, presupuesto y tipo de combustible.")

# --- Carga de Datos y Preprocesamiento ---
@st.cache_data # Cachear la carga y limpieza de datos para mejorar el rendimiento
def load_and_clean_data(file_path):
    df = pd.read_csv(file_path)
    
    # Rellenar valores nulos
    # Para `model_year`, `cylinders`, `odometer` y `paint_color`, usar la moda o el promedio si es adecuado
    df['model_year'] = df['model_year'].fillna(df['model_year'].median())
    df['cylinders'] = df['cylinders'].fillna(df['cylinders'].mode()[0])
    df['odometer'] = df['odometer'].fillna(df['odometer'].median())
    
    # Rellenar nulos con 'unknown' para categorías
    for col in ['paint_color', 'is_4wd', 'condition', 'fuel', 'transmission']:
        df[col] = df[col].fillna('unknown')
        
    # Asignación de Marca (Mejorado)
    # Lista de marcas a considerar
    marcas_base = ['ford', 'hyundai', 'bmw', 'honda', 'toyota', 'chevrolet', 'ram']
    df['marca'] = np.nan # Inicializar la columna 'marca' con NaN
    
    # Usar expresiones regulares para buscar todas las marcas a la vez de forma eficiente
    regex_pattern = '|'.join([f'({m})' for m in marcas_base])
    
    # Aplicar una función para encontrar la primera coincidencia
    def find_marca(model):
        if pd.isna(model):
            return np.nan
        for marca in marcas_base:
            if marca in model.lower():
                return marca.capitalize() # Capitalizar el nombre de la marca
        return 'Otras' # Asignar 'Otras' si no coincide con las marcas clave
        
    df['marca'] = df['model'].apply(find_marca)
    
    # Filtrar solo registros con una marca asignada (excluir Nans y 'Otras' si se desea, o solo 'Otras')
    # Para este ejemplo, solo nos interesan las marcas_base y las nombramos en mayúscula para distinguirlas
    df = df[df['marca'].isin([m.capitalize() for m in marcas_base])]
    
    return df

df = load_and_clean_data('vehicles_us.csv')
marcas_disponibles = sorted(df['marca'].unique().tolist()) # Obtener marcas únicas y limpias

# --- Barra Lateral para Filtros Principales (Mejor UX) ---
with st.sidebar:
    st.header("⚙️ Filtros de Búsqueda")
    
    # 1. Selección de Marcas
    marca_select = st.multiselect(
        'Selecciona Marcas:', 
        options=marcas_disponibles, 
        default=marcas_disponibles,
        key='marca_filtro'
    )
    
    # 2. Selección de Presupuesto
    max_price = int(df['price'].max())
    slider_precio = st.slider(
        'Presupuesto Máximo (Precio)',
        min_value=0, 
        max_value=max_price, # Usar el máximo real de los datos
        step=500, 
        value=min(25000, max_price), # Valor por defecto más realista
        key='precio_filtro'
    )
    
    # 3. Selección de Combustible (Usamos `pills` dentro del sidebar para un diseño compacto)
    fuel_options = df['fuel'].unique().tolist()
    gass_select = st.multiselect(
        "Tipos de Combustible:", 
        options=fuel_options, 
        default=fuel_options,
        key='combustible_filtro'
    )
    
    # Botón/Checkbox para el Histograma
    st.subheader("Visualizaciones")
    hist_box = st.checkbox('Mostrar Histograma de Precios', value=True)
    
# --- Aplicar Filtrado de Datos ---
# Se recomienda un único bloque de filtrado para mayor claridad
df_filtrado = df[
    (df['marca'].isin(marca_select)) & 
    (df['price'] <= slider_precio) & 
    (df['fuel'].isin(gass_select))
]

# --- Visualizaciones y Resultados ---

if df_filtrado.empty:
    st.warning("⚠️ **No hay vehículos que coincidan con los filtros seleccionados.** Intenta modificar tu presupuesto, marca o tipo de combustible.")
else:
    
    # 1. Histograma Condicional
    if hist_box:
        st.subheader(f'Histograma de Precios por Marca (Máx: ${slider_precio:,.0f})')
        # Usar `st.container` y `st.columns` para ordenar la visualización
        col1, col2 = st.columns([2, 1])
        with col1:
            fig, ax = plt.subplots(figsize=(8, 5))
            
            # Iterar sobre las marcas seleccionadas y no sobre todas las del df_filtrado
            for marca in marca_select:
                data_plot = df_filtrado[df_filtrado['marca'] == marca]
                sns.histplot(
                    data=data_plot, 
                    x='price', 
                    ax=ax, 
                    label=marca, 
                    alpha=0.6, 
                    kde=True, # Añadir KDE para suavizar la distribución
                    bins=20 # Definir un número de bins
                )
            
            # Configuración final del gráfico
            ax.legend(title='Marca')
            ax.set_title('Distribución de Precios de Vehículos Seleccionados')
            ax.set_xlabel('Precio (USD)')
            ax.set_ylabel('Frecuencia')
            ax.set_xlim((0, slider_precio * 1.05)) # Ajustar el límite X al presupuesto
            st.pyplot(fig)
        
        with col2:
            st.metric("Total de Vehículos Encontrados", f"{len(df_filtrado):,}")
            # Muestra el precio promedio en el rango filtrado
            st.metric("Precio Promedio", f"${df_filtrado['price'].mean():,.0f}")
        
        st.markdown("---")


    # 2. Scatter Plot (Dispersión)
    st.subheader('Relación entre Odómetro y Precio')
    st.markdown("Visualiza cómo el **kilometraje (odómetro)** impacta el **precio** de los vehículos.")
    
    # Crear el gráfico de dispersión con Plotly Express
    figa = px.scatter(
        df_filtrado, 
        x='odometer', 
        y='price', 
        color='marca', # Usar la marca como color
        hover_data=['model', 'condition', 'model_year'], # Datos que aparecen al pasar el ratón
        title="Odómetro vs. Precio, coloreado por Marca",
        labels={'odometer': 'Kilometraje (Odómetro)', 'price': 'Precio (USD)'}
    )
    
    # Ajustar el rango del eje Y al presupuesto máximo
    figa.update_yaxes(range=[0, slider_precio * 1.05]) 
    st.plotly_chart(figa, use_container_width=True)
    
    st.markdown("---")

    # 3. Presentación de la Información Filtrada (Tabla)
    st.subheader(f'Listado de Vehículos Encontrados ({len(df_filtrado)} resultados)')
    st.dataframe(df_filtrado, use_container_width=True)
