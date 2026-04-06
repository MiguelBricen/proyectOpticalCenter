import streamlit as st
import requests

st.title("🌦️ Clima en tiempo real")

ciudades_nicaragua = {
    "Managua": [
        "Managua", "Tipitapa", "San Rafael del Sur"
    ],
    "León": [
        "León", "Nagarote", "La Paz Centro", "Telica", "Quezalguaque"
    ],
    "Chinandega": [
        "Chinandega", "Corinto", "Chichigalpa", "El Viejo", "Somotillo"
    ],
    "Granada": [
        "Granada", "Nandaime", "Diriá", "Diriomo"
    ],
    "Masaya": [
        "Masaya", "Nindirí", "Tisma", "La Concepción", "Masatepe"
    ],
    "Carazo": [
        "Jinotepe", "Diriamba", "San Marcos", "Dolores"
    ],
    "Rivas": [
        "Rivas", "San Juan del Sur", "Tola", "Belén", "Potosí"
    ],
    "Matagalpa": [
        "Matagalpa", "San Ramón", "Sébaco", "San Isidro"
    ],
    "Jinotega": [
        "Jinotega", "San Juan de Río Coco", "La Concordia"
    ],
    "Estelí": [
        "Estelí", "Condega", "San Juan de Río Coco"
    ],
    "Nueva Segovia": [
        "Ocotal", "Quilalí", "Macuelizo", "Dipilto"
    ],
    "Madriz": [
        "Somoto", "Palacagüina", "San Juan de Río Coco"
    ],
    "Boaco": [
        "Boaco", "Camoapa", "San José de los Remates"
    ],
    "Chontales": [
        "Juigalpa", "Acoyapa", "Santo Tomás"
    ],
    "Río San Juan": [
        "San Carlos", "San Miguelito", "Morrito"
    ],
    "RAAN": [
        "Puerto Cabezas", "Siuna", "Waspam"
    ],
    "RAAS": [
        "Bluefields", "Nueva Guinea", "Kukra Hill"
    ]
}

departamento = st.selectbox("Seleccione departamento", list(ciudades_nicaragua.keys()))

ciudad = st.selectbox("Seleccione ciudad", ciudades_nicaragua[departamento])

API_KEY = "d63f14551b1110d1dc859aa3c03d28e0"

if st.button("Buscar"):
    
    if ciudad.strip() == "":
        st.warning("⚠️ Por favor ingrese una ciudad")
    else:
        # Forzar país Nicaragua
        url = f"https://api.openweathermap.org/data/2.5/weather?q={ciudad},NI&appid={API_KEY}&units=metric&lang=es"
        
        try:
            respuesta = requests.get(url)
            data = respuesta.json()

            if respuesta.status_code == 200:
                st.success(f"Clima en {data['name']}")

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("🌡️ Temperatura", f"{data['main']['temp']} °C")

                with col2:
                    st.metric("💧 Humedad", f"{data['main']['humidity']}%")

                with col3:
                    st.metric("☁️ Clima", data['weather'][0]['description'])

            else:
                st.error(f"❌ Error: {data.get('message', 'Ciudad no encontrada')}")

        except Exception as e:
            st.error(f"Error de conexión: {e}")