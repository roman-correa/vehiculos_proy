import pandas as pd
import plotly.express as px
import streamlit as st

df = pd.read_csv('vehicles_us.csv')  # leer los datos
# st.header("ALGO NO ME FUNCIONA")

marcas = ['ford', 'hyundai', 'bmw', 'honda', 'toyota', 'chevrolet', 'ram']
marca_select = st.selectbox('Selecciones una marca:', marcas)


hist_box = st.checkbox('Construir histograma')  # crear un botón
patron_busqueda = '|'.join(marca_select)
mrc= df.query('model.str.contains(@patron_busqueda)')
if hist_box:  # al hacer clic en el botón
    # escribir un mensaje
    st.write(
        'Creación de un histograma para el conjunto de datos de anuncios de venta de coches')

    # crear un histograma
    fig = px.histogram(mrc, x="price")

    # mostrar un gráfico Plotly interactivo
    st.plotly_chart(fig, use_container_width=True)
