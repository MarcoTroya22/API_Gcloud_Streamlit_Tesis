import streamlit as st
import time
import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestRegressor
import mysql.connector
import pandas as pd
import plotly.express as px

# Configuración de la conexión a la base de datos MySQL
db_config = {
    'host': 'localhost',
    'user': 'tesisesp32',
    'password': 'tesisMLMT',
    'database': 'tesis_db'
}

# Cargar los modelos entrenados
modelo_regresion_logistica = joblib.load('models/modelo_regresion_logistica.pkl')
modelo_random_forest = joblib.load(open('models/modelo_random_forest.pkl', 'rb'))

# Se recibe la Temperatura del Motor y el Campo Magnético, devuelve la predicción
def model_prediction_logistica(Temperatura_Motor, Campo_Magnetico):
    return modelo_regresion_logistica.predict([[Temperatura_Motor, Campo_Magnetico]])[0]

# Se recibe la Temperatura del Motor y el Campo Magnético, devuelve la predicción
def model_prediction_random_forest(Temperatura_Motor, Campo_Magnetico):
    return modelo_random_forest.predict([[Temperatura_Motor, Campo_Magnetico]])[0]

# Función para obtener datos de la base de datos con caché
@st.cache_data(ttl=30)  # caché con un tiempo de vida de 30 segundos
def get_data_from_database(device):
    try:
        with mysql.connector.connect(**db_config) as conn:
            cursor = conn.cursor()
            query = f"SELECT Tiempo, Temperatura_Motor, Campo_Magnetico FROM data_sensores_ml1 WHERE Device = '{device}' ORDER BY Tiempo"
            print(f"Ejecutando consulta: {query}")
            cursor.execute(query)
            data = cursor.fetchall()
            df = pd.DataFrame(data, columns=['Tiempo', 'Temperatura_Motor', 'Campo_Magnetico'])
        return df
    except mysql.connector.Error as err:
        print(f"Error: {err}")

# Función para verificar la autenticación
def authenticate(username, password):
    return username == 'Marco Troya' and password == 'Tesis1234'

# Ventana de autenticación
def authentication():
    st.title("Ingreso de Autenticación")
    username = st.text_input("Usuario:")
    password = st.text_input("Contraseña:", type="password")
    if st.button("Ingresar"):
        if authenticate(username, password):
            st.session_state.authenticated = True
        else:
            st.error("Autenticación fallida. Verifica tus credenciales.")

# Ventana de visualización y predicción
# Ventana de visualización y predicción
def visualization(device):
    # Título
    html_temp = f"""
    <h1 style="color:#0000FF; text-align:center; width: 100%; font-size: 29px;">Sistema de Monitoreo para la Estación Conveyor MPS-500 y aplicación de Mantenimiento Predictivo utilizando Inteligencia Artificial para el Motor {device} </h1>
    """
    st.markdown(html_temp, unsafe_allow_html=True)

    # Obtener datos de la base de datos
    data = get_data_from_database(device)

    # Graficar Temperatura en función del tiempo
    fig_temp = px.line(data, x='Tiempo', y='Temperatura_Motor', title=f'Temperatura del Motor {device} en función del tiempo')
    fig_temp.update_traces(line_color='red')
    st.plotly_chart(fig_temp)

    # Graficar Campo Magnético en función del tiempo
    fig_campo = px.line(data, x='Tiempo', y='Campo_Magnetico', title=f'Campo Magnético del Motor {device} en función del tiempo')
    fig_campo.update_traces(line_color='purple')
    st.plotly_chart(fig_campo)

    # Último valor de la Temperatura y Campo Magnético
    latest_temp = data['Temperatura_Motor'].iloc[-1]
    latest_campo = data['Campo_Magnetico'].iloc[-1]

    # Mostrar el último valor de la Temperatura en un cuadro
    st.text(f'Temperatura {device}: {latest_temp}')

    # Mostrar el último valor de Campo Magnético en un cuadro
    st.text(f'Campo Magnético {device}: {latest_campo}')

    # El botón predicción se usa para iniciar el procesamiento
    if st.button(f"Predicción para Motor {device} :"): 
        # Realizar la predicción con el modelo de regresión logística
        prediccion_logistica = model_prediction_logistica(latest_temp, latest_campo)

        if prediccion_logistica == 0:
            st.success('Funcionamiento normal')
        else:
            # Realizar la predicción con el modelo Random Forest
            prediccion_random_forest = model_prediction_random_forest(latest_temp, latest_campo)
            st.error(f'ALERTA MANTENIMIENTO: el tiempo restante hasta un posible fallo es de {prediccion_random_forest} días')

# Función principal
def main():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        authentication()
    else:
        devices = ["M1", "M2", "M3", "M4"]
        
        # Utilizar st.sidebar para agregar elementos en la barra lateral
        st.sidebar.button("Finalizar Sesión", on_click=lambda: st.session_state.update({"authenticated": False}))
        
        # Agregar el contenido principal en la sección central
        for device in devices:
            visualization(device)
            st.empty()  # Espacio en blanco para futuras actualizaciones

if __name__ == '__main__':
    main()
