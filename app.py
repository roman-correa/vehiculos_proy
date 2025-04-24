import pandas as pd
import plotly.express as px
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt

df = pd.read_csv('vehicles_us.csv')  # leer los datos
# st.header("ALGO NO ME FUNCIONA")

marcas = ['ford', 'hyundai', 'bmw', 'honda', 'toyota', 'chevrolet', 'ram']
marca_select = st.multiselect(
    'Selecciones una marca:', options=marcas, default=marcas)
for i in marca_select:
    df.loc[df['model'].str.contains(i, case=False, na=False), 'marca'] = i


df_filt = df[df['marca'].isin(marca_select)]
hist_box = st.checkbox('Construir histograma')  # crear un botón
if 'hist_box' not in st.session_state:
    st.session_state.hist_box = False


if hist_box:
    st.session_state.hist_box = True
    if st.session_state.hist_box:
        if not df_filt.empty:
            fig, ax = plt.subplots(figsize=(8, 5))
            for i in marca_select:
                sns.histplot(data=df_filt[df_filt['marca']
                            == i], x='price', ax=ax, label=i)
            ax.legend(title='Marca')
            ax.set_xlim((0, 70000))
            st.pyplot(fig)



slider_precio = st.slider('Selecciones su presupuesto', min_value = 0, max_value = 70000, step=1)

if 'slider_precio' not in st.session_state:
    st.session_state.slicer_precio = False
if slider_precio:
    st.session_state.slicer_precio = True
if st.session_state.slicer_precio:

    df_dos = df_filt[df_filt['price'] <= slider_precio]
    df_dos

fuel_filt = df['fuel'].unique()
gass = st.pills("Combustible", fuel_filt, selection_mode="multi")
if 'gass' not in st.session_state:
    st.session_state.gass = False

if gass:
    st.session_state.gass = True
if st.session_state.gass:
    df_tres = df_dos.query('fuel in @gass')
    df_tres
