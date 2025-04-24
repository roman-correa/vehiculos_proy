import pandas as pd
import plotly.express as px
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt

df = pd.read_csv('vehicles_us.csv')  # leer los datos
st.header('**VEHICULOS EN VENTA**')
st.subheader('Selecciones tantas marcas commo desee')

# definicion de un primer filtro manual para sacar las marcas de la columna 'model'
marcas = ['ford', 'hyundai', 'bmw', 'honda', 'toyota', 'chevrolet', 'ram']

# crea un cuadro de seleccion de marcas, por defecto 'todas' seleccionadas
marca_select = st.multiselect(
    'Selecciones una marca:', options=marcas, default=marcas)

# crea una columna nueva buscando en la columna de 'model' las coincidencias con el filtro de marcas
for i in marca_select:
    df.loc[df['model'].str.contains(i, case=False, na=False), 'marca'] = i

# Dataframe nuevo solo con las coincidencias en el filtro
df_filt = df[df['marca'].isin(marca_select)]
# crear un cuadro de seleccion
hist_box = st.checkbox('Construir histograma')
# ingresa al sessionstate la variable de seleccion 'hist_box'
if 'hist_box' not in st.session_state:
    st.session_state.hist_box = False

# si presiona el boton entonces sessionstate del boton se activa y muestra histograma de los datos filtrados
if hist_box:
    st.session_state.hist_box = True
    if st.session_state.hist_box:
        # si el dataframe filtrado no esta vacio entonces crea una figura y las llena con los datos de las marcas que desea ver el usuario
        if not df_filt.empty:
            fig, ax = plt.subplots(figsize=(8, 5))
            for i in marca_select:
                sns.histplot(data=df_filt[df_filt['marca']
                                          == i], x='price', ax=ax, label=i, alpha=0.4)
            ax.legend(title='Marca')
            ax.set_xlim((0, 70000))
            st.pyplot(fig)

# slider con el presupuesto del cliente para filtrar los vehiculos previamente filtrado por marcas
slider_precio = st.slider('Selecciones su presupuesto',
                          min_value=0, max_value=70000, step=1, value=20000)

# presentacion de la informacion filtrada por marca y presupuesto
if 'slider_precio' not in st.session_state:
    st.session_state.slicer_precio = False
if slider_precio:
    st.session_state.slicer_precio = True

    if st.session_state.slicer_precio:
        st.subheader('Informacion filtrada por marca y presupuesto')

        df_dos = df_filt[df_filt['price'] <= slider_precio]
        df_dos

# seleccion de combustible
fuel_filt = df['fuel'].unique()
gass = st.pills("Combustible", fuel_filt, selection_mode="multi")
if 'gass' not in st.session_state:
    st.session_state.gass = False

# presentacion de la informacion filtrada por marca, presupuesto y combustible y un scatterplot
if gass:
    st.session_state.gass = True
    if st.session_state.gass:
        st.subheader(
            'Informacion filtrada por marca, presupuesto y combustible')
        df_tres = df_dos.query('fuel in @gass')
        df_tres

        # sns.scatterplot(df_tres, x="odometer", y="price", hue = 'marca')
        figa = px.scatter(df_tres, x='odometer', y='price',
                          range_y=([0, slider_precio]))
        st.plotly_chart(figa)
