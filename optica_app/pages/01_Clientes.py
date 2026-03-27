import streamlit as st
import pandas as pd
from utils.helpers import fetch_data, execute_query, check_auth
from utils.ui_components import header_ui

# Verificación de Autenticación
if not check_auth():
    st.warning("⚠️ Acceso denegado. Por favor, inicie sesión en la página principal.")
    st.stop()

st.set_page_config(page_title="Clientes | Óptica Stefany", page_icon="👥", layout="wide")
header_ui("Gestión de Clientes", "Registrar, consultar, editar y eliminar clientes")

# Función para formatear el DataFrame a mostrar
def formatear_clientes(df):
    if df.empty:
        return df
    df_mostrar = df.copy()
    if 'id' in df_mostrar.columns:
        df_mostrar = df_mostrar.drop(columns=['id'])
    
    nuevo_formato = {
        'nombre': 'NOMBRE',
        'cedula': 'CÉDULA',
        'telefono': 'TELÉFONO'
    }
    df_mostrar = df_mostrar.rename(columns=nuevo_formato)
    return df_mostrar

tab1, tab2, tab3, tab4 = st.tabs(["Listado de Clientes", "Registrar Cliente", "Editar Cliente", "Eliminar Cliente"])

with tab1:
    st.write("### 🔍 Buscar y Consultar Clientes")
    search_term = st.text_input("Buscar cliente por nombre (insensible a mayúsculas):")
    
    if search_term:
        query = "SELECT id, nombre, cedula, telefono FROM Clientes WHERE LOWER(nombre) LIKE LOWER(?)"
        df = fetch_data(query, (f"%{search_term}%",))
    else:
        query = "SELECT id, nombre, cedula, telefono FROM Clientes"
        df = fetch_data(query)
        
    if not df.empty:
        df_mostrar = formatear_clientes(df)
        st.dataframe(df_mostrar, use_container_width=True, hide_index=True)
    else:
        st.info("No hay clientes registrados o no hay coincidencias con la búsqueda.")

with tab2:
    st.write("### ➕ Nuevo Cliente")
    with st.form("registro_cliente_form", clear_on_submit=True):
        nombre = st.text_input("Nombre Completo *")
        cedula = st.text_input("Cédula (Opcional)")
        telefono = st.text_input("Teléfono *")
        
        submitted = st.form_submit_button("Guardar Cliente")
        
        if submitted:
            if not nombre.strip() or not telefono.strip():
                st.error("❌ Los campos 'Nombre Completo' y 'Teléfono' son obligatorios.")
            else:
                # Verificar duplicados
                check_query = "SELECT id FROM Clientes WHERE LOWER(nombre) = LOWER(?) AND telefono = ?"
                duplicate_df = fetch_data(check_query, (nombre.strip(), telefono.strip()))
                
                if not duplicate_df.empty:
                    st.warning("⚠️ Ya existe un cliente registrado con ese nombre y teléfono.")
                else:
                    try:
                        execute_query(
                            "INSERT INTO Clientes (nombre, cedula, telefono) VALUES (?, ?, ?)", 
                            (nombre.strip(), cedula.strip() if cedula.strip() else None, telefono.strip())
                        )
                        st.success("✅ Cliente registrado correctamente.")
                        st.cache_data.clear()
                    except Exception as e:
                        st.error(f"❌ Error al registrar: {e}")

with tab3:
    st.write("### ✏️ Editar Cliente")
    df_clientes = fetch_data("SELECT id, nombre, cedula, telefono FROM Clientes")
    
    if df_clientes.empty:
        st.info("No hay clientes registrados para editar.")
    else:
        opciones_clientes = {
            f"{row['nombre']} - {row['telefono']}": row['id'] 
            for _, row in df_clientes.iterrows()
        }
        
        cliente_seleccionado = st.selectbox("Seleccione el cliente a editar:", list(opciones_clientes.keys()))
        
        if cliente_seleccionado:
            cliente_id = opciones_clientes[cliente_seleccionado]
            datos_cliente = df_clientes[df_clientes['id'] == cliente_id].iloc[0]
            
            with st.form("edicion_cliente_form"):
                st.write(f"Editando a: **{datos_cliente['nombre']}**")
                
                edit_nombre = st.text_input("Nombre Completo *", value=datos_cliente['nombre'])
                edit_cedula = st.text_input("Cédula (Opcional)", value=datos_cliente['cedula'] if pd.notna(datos_cliente['cedula']) and datos_cliente['cedula'] else "")
                edit_telefono = st.text_input("Teléfono *", value=datos_cliente['telefono'])
                
                sub_edit = st.form_submit_button("Actualizar cliente")
                
                if sub_edit:
                    if not edit_nombre.strip() or not edit_telefono.strip():
                        st.error("❌ Los campos 'Nombre Completo' y 'Teléfono' son obligatorios.")
                    else:
                        try:
                            execute_query(
                                "UPDATE Clientes SET nombre = ?, cedula = ?, telefono = ? WHERE id = ?",
                                (edit_nombre.strip(), edit_cedula.strip() if edit_cedula.strip() else None, edit_telefono.strip(), cliente_id)
                            )
                            st.success("✅ Cliente actualizado correctamente.")
                            st.cache_data.clear()
                        except Exception as e:
                            st.error(f"❌ Error al actualizar: {e}")

with tab4:
    st.write("### 🗑️ Eliminar Cliente")
    if df_clientes.empty:
        st.info("No hay clientes registrados para eliminar.")
    else:
        cliente_del_sel = st.selectbox("Seleccione el cliente a eliminar:", list(opciones_clientes.keys()), key="select_del")
        
        if cliente_del_sel:
            cliente_id_del = opciones_clientes[cliente_del_sel]
            
            with st.form("eliminar_cliente_form"):
                st.warning(f"¿Estás seguro de eliminar el cliente **{cliente_del_sel.split(' - ')[0]}**?")
                st.write("Esta acción no se puede deshacer.")
                confirmacion = st.checkbox("Sí, confirmo que deseo eliminar este cliente.")
                
                sub_del = st.form_submit_button("Eliminar cliente", type="primary")
                
                if sub_del:
                    if confirmacion:
                        try:
                            execute_query("DELETE FROM Clientes WHERE id = ?", (cliente_id_del,))
                            st.success("✅ Cliente eliminado correctamente.")
                            st.cache_data.clear()
                        except Exception as e:
                            st.error(f"❌ Error al eliminar: {e}")
                    else:
                        st.error("⚠️ Debes marcar la casilla de confirmación para eliminar al cliente.")
