import streamlit as st
import pandas as pd
from utils.helpers import fetch_data, execute_query, check_auth
from utils.ui_components import header_ui
from datetime import date

# Verificación de Autenticación y Rol
if not check_auth():
    st.warning("⚠️ Acceso denegado. Por favor, inicie sesión en la página principal.")
    st.stop()

if st.session_state.role != "Administrador":
    st.error("🚫 No tiene permisos para acceder a esta sección.")
    st.stop()

st.set_page_config(page_title="Trabajadores | Óptica Stefany", page_icon="👷", layout="wide")
header_ui("Gestión de Trabajadores", "Plantilla y control de horas")

tab1, tab2, tab3 = st.tabs(["Personal", "Control de Horas", "Cálculo de Pago"])

with tab1:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.write("### Registrar Trabajador")
        with st.form("registro_trabajador_form", clear_on_submit=True):
            nombre = st.text_input("Nombre Completo *")
            cargo = st.text_input("Cargo *")
            telefono = st.text_input("Teléfono *")
            
            sub_trabajador = st.form_submit_button("Guardar")
            if sub_trabajador:
                if not nombre or not cargo or not telefono:
                    st.error("Todos los campos marcados con * son obligatorios.")
                else:
                    try:
                        execute_query("INSERT INTO Trabajadores (nombre, cargo, telefono) VALUES (?, ?, ?)", (nombre, cargo, telefono))
                        st.success("Trabajador registrado.")
                        st.cache_data.clear()
                    except Exception as e:
                        st.error(f"Error: {e}")
                        
    with col2:
        st.write("### Nómina Actual")
        df_trab = fetch_data("SELECT id, nombre, cargo, telefono FROM Trabajadores")
        if not df_trab.empty:
            df_mostrar_trab = df_trab.drop(columns=['id'])
            nuevo_formato_trab = {
                'nombre': 'NOMBRE',
                'cargo': 'CARGO',
                'telefono': 'TELÉFONO'
            }
            df_mostrar_trab = df_mostrar_trab.rename(columns=nuevo_formato_trab)
            st.dataframe(df_mostrar_trab, use_container_width=True, hide_index=True)
        else:
            st.info("No hay trabajadores registrados.")

with tab2:
    st.write("### Registro de Horas")
    df_trab_all = fetch_data("SELECT * FROM Trabajadores")
    if df_trab_all.empty:
        st.warning("Debe registrar al menos un trabajador para controlar horas.")
    else:
        trabajadores_dict = {row["nombre"]: row["id"] for _, row in df_trab_all.iterrows()}
        with st.form("horas_form", clear_on_submit=True):
            trabajador_sel = st.selectbox("Trabajador *", list(trabajadores_dict.keys()))
            fecha_horas = st.date_input("Fecha *", value=date.today())
            horas = st.number_input("Horas Trabajadas *", min_value=0.1, value=8.0, step=0.5)
            obs = st.text_area("Observaciones")
            
            sub_horas = st.form_submit_button("Registrar Horas")
            if sub_horas:
                if horas <= 0:
                    st.error("Las horas deben ser mayores a cero.")
                else:
                    try:
                        t_id = trabajadores_dict[trabajador_sel]
                        execute_query(
                            "INSERT INTO Horas_trabajo (trabajador_id, fecha, horas, observaciones) VALUES (?, ?, ?, ?)",
                            (t_id, fecha_horas.strftime("%Y-%m-%d"), horas, obs)
                        )
                        st.success("Horas registradas correctamente.")
                        st.cache_data.clear()
                    except Exception as e:
                        st.error(f"Error: {e}")

with tab3:
    st.write("### Calcular Pago")
    df_trab_all_2 = fetch_data("SELECT * FROM Trabajadores")
    if not df_trab_all_2.empty:
        trabajadores_dict = {row["nombre"]: row["id"] for _, row in df_trab_all_2.iterrows()}
        col3, col4 = st.columns(2)
        with col3:
            trabajador_pago_sel = st.selectbox("Seleccione Trabajador", list(trabajadores_dict.keys()), key="pago_sel")
        with col4:
            pago_por_hora = st.number_input("Pago por Hora ($)", min_value=0.1, value=10.0, step=0.5)
            
        t_id_pago = trabajadores_dict[trabajador_pago_sel]
        df_horas = fetch_data("SELECT SUM(horas) as total_horas FROM Horas_trabajo WHERE trabajador_id = ?", (t_id_pago,))
        
        total_horas_val = 0
        if not df_horas.empty and df_horas.iloc[0]["total_horas"] is not None:
            total_horas_val = df_horas.iloc[0]["total_horas"]
            
        st.metric(label=f"Total Horas Registradas para {trabajador_pago_sel}", value=f"{total_horas_val} h")
        
        pago_total = total_horas_val * pago_por_hora
        st.success(f"**Monto a pagar:** ${pago_total:,.2f}")
        
        st.write("#### Historial de horas")
        df_historial = fetch_data("SELECT fecha, horas, observaciones FROM Horas_trabajo WHERE trabajador_id = ? ORDER BY fecha DESC", (t_id_pago,))
        if not df_historial.empty:
            st.dataframe(df_historial, use_container_width=True, hide_index=True)
        else:
            st.info("No hay registros de horas para este trabajador.")
