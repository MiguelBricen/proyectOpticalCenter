import streamlit as st
from utils.helpers import fetch_data, execute_query, check_auth
from utils.ui_components import header_ui

# Verificación de Autenticación
if not check_auth():
    st.warning("⚠️ Acceso denegado. Por favor, inicie sesión en la página principal.")
    st.stop()

st.set_page_config(page_title="Inventario | Óptica Stefany", page_icon="📦", layout="wide")
header_ui("Control de Inventario", "Gestionar productos de la óptica")

tab1, tab2 = st.tabs(["Consultar Inventario", "Registrar Producto"])

with tab1:
    col1, _ = st.columns([1, 2])
    with col1:
        filtro_cat = st.selectbox("Filtrar por Categoría", ["Todas", "A (Lujo)", "B (Intermedio)", "C (Económico)", "D (Marco propio)", "E (Accesorios)"])
    
    query = "SELECT * FROM Inventario"
    params = ()
    if filtro_cat != "Todas":
        cat_letra = filtro_cat[0] # Obtiene la primera letra
        query += " WHERE categoria = ?"
        params = (cat_letra,)
        
    df = fetch_data(query, params)
    
    if not df.empty:
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No hay productos en esta categoría o el inventario está vacío.")

with tab2:
    with st.form("registro_producto_form", clear_on_submit=True):
        st.write("### Nuevo Producto")
        nombre = st.text_input("Nombre del producto *")
        categoria = st.selectbox("Categoría *", ["A (Lujo)", "B (Intermedio)", "C (Económico)", "D (Marco propio)", "E (Accesorios)"])
        cantidad = st.number_input("Cantidad *", min_value=1, value=1, step=1)
        precio = st.number_input("Precio ($) *", min_value=0.0, value=0.0, step=0.1)
        
        submitted = st.form_submit_button("Guardar Producto")
        
        if submitted:
            if not nombre:
                st.error("El nombre del producto es obligatorio.")
            elif precio <= 0:
                st.error("El precio debe ser mayor a 0.")
            else:
                try:
                    cat_letra = categoria[0]
                    execute_query(
                        "INSERT INTO Inventario (nombre, categoria, cantidad, precio) VALUES (?, ?, ?, ?)",
                        (nombre, cat_letra, cantidad, precio)
                    )
                    st.success("Producto registrado con éxito.")
                    st.cache_data.clear()
                except Exception as e:
                    st.error(f"Error al registrar: {e}")
