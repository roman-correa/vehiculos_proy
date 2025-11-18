# 🚗 Dashboard Interactivo de Vehículos en Venta 

## 📝 Descripción del Proyecto

Este proyecto presenta un **Dashboard Interactivo** construido con **Streamlit** y **Python** para el análisis exploratorio de datos (EDA) sobre listados de vehículos usados. Permite a los usuarios filtrar la información por **Marca**, **Presupuesto Máximo** y **Tipo de Combustible** para visualizar la distribución de precios y la relación entre el precio y el kilometraje (odómetro) de manera dinámica.

## ✨ Características Principales

* **Filtros Dinámicos:** Utiliza la barra lateral de Streamlit para una experiencia de filtrado intuitiva y eficiente.
* **Limpieza de Datos:** Implementación de `@st.cache_data` para el preprocesamiento, manejo de valores nulos (NaN) y asignación eficiente de marcas.
* **Visualizaciones Clave:**
    * **Histograma de Precios:** Muestra la distribución de precios por marca dentro del rango presupuestado (generado con `matplotlib` y `seaborn`).
    * **Gráfico de Dispersión (Scatter Plot):** Analiza la correlación entre **Odómetro (Kilometraje)** y **Precio** (generado con `Plotly Express`).
* **Métricas en Tiempo Real:** Proporciona un resumen instantáneo del total de vehículos encontrados y el precio promedio según los filtros aplicados.

## 🛠️ Tecnologías Utilizadas

| Tecnología | Rol |
| :--- | :--- |
| **Python** | Lenguaje de programación principal. |
| **Streamlit** | Framework para construir la interfaz de usuario interactiva (Dashboard). |
| **Pandas** | Manipulación y limpieza de datos (DataFrame). |
| **Plotly Express** | Creación de gráficos interactivos (Scatter Plot). |
| **Matplotlib / Seaborn** | Creación de gráficos estáticos de distribución (Histograma). |

## 🚀 Instalación y Ejecución Local

Para ejecutar este dashboard en tu máquina local, sigue los siguientes pasos:

### 1. Clonar el Repositorio

```bash
git clone <URL_DE_TU_REPOSITORIO>
cd <NOMBRE_DEL_DIRECTORIO>
