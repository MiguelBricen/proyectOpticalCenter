import streamlit as st
from utils.helpers import fetch_data, execute_query, check_auth
from utils.ui_components import header_ui
from datetime import date

# Verificación de Autenticación
if not check_auth():
    st.warning("⚠️ Acceso denegado. Por favor, inicie sesión en la página principal.")
    st.stop()

st.set_page_config(page_title="Ventas y Reservaciones | Óptica Stefany", page_icon="💸", layout="wide")
header_ui("Registro de Ventas y Reservaciones", "Administrar ventas, abonos y cobros")

# --- FUNCIONES DE FACTURACIÓN ---
def generar_factura(venta_id, monto, tipo="Digital"):
    fecha = date.today().strftime("%Y-%m-%d %H:%M:%S")
    execute_query(
        "INSERT INTO Facturas (venta_id, fecha, tipo, monto_total) VALUES (?, ?, ?, ?)",
        (venta_id, fecha, tipo, monto)
    )
    return fecha

def mostrar_factura_ui(venta_id, cliente, producto, precio, fecha, tipo="Digital"):
    st.markdown(f"""
    <div style="border: 2px solid #007bff; padding: 20px; border-radius: 10px; background-color: white; color: #333; font-family: monospace;">
        <h2 style="text-align: center; color: #007bff;">📄 ÓPTICA STEFANY</h2>
        <p style="text-align: center;">Factura {tipo} | ID Venta: {venta_id}</p>
        <hr>
        <p><b>Fecha:</b> {fecha}</p>
        <p><b>Cliente:</b> {cliente}</p>
        <p><b>Producto:</b> {producto}</p>
        <hr>
        <h3 style="text-align: right;">TOTAL: ${precio:.2f}</h3>
        <p style="font-size: 0.8rem; text-align: center; color: #999;">¡Gracias por su confianza en nuestra salud visual!</p>
    </div>
    """, unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["Reservaciones", "Nueva Venta", "Historial de Ventas", "Historial de Facturas"])

categorias_disp = ["A (Lujo)", "B (Intermedio)", "C (Económico)", "D (Marco propio)", "E (Accesorios)"]

with tab1:
    st.write("### 📅 Gestión de Reservaciones (Abonos)")
    
    # Cargar clientes
    clientes_df = fetch_data("SELECT id, nombre, telefono FROM Clientes")
    if clientes_df.empty:
        st.warning("⚠️ No hay clientes registrados para hacer una reservación.")
    else:
        clientes_dict = {f"{row['nombre']} - {row['telefono']}": row["id"] for _, row in clientes_df.iterrows()}
        clientes_nombres = list(clientes_dict.keys())
        
        col_res1, col_res2 = st.columns(2)
        with col_res1:
            st.write("#### ✨ Nueva Reservación")
            with st.form("registro_reserva_form", clear_on_submit=True):
                cliente_res = st.selectbox("Cliente *", clientes_nombres, key="res_cliente")
                producto_res = st.text_input("Producto *", key="res_prod")
                categoria_res = st.selectbox("Categoría *", categorias_disp, key="res_cat")
                precio_res = st.number_input("Precio Total ($) *", min_value=0.0, value=0.0, step=0.1, key="res_prec")
                abono_ini = st.number_input("Abono Inicial ($) *", min_value=0.0, value=0.0, step=0.1, key="res_abono")
                desc_res = st.text_area("Descripción *", key="res_desc")
                
                sub_reserva = st.form_submit_button("Registrar Reservación")
                if sub_reserva:
                    if not producto_res or not desc_res or precio_res <= 0:
                        st.error("Campos con * son obligatorios y el precio debe ser mayor a 0.")
                    elif abono_ini > precio_res:
                        st.error("El abono inicial no puede ser mayor al precio total.")
                    else:
                        try:
                            c_id = clientes_dict[cliente_res]
                            cat_l = categoria_res[0]
                            f_act = date.today().strftime("%Y-%m-%d")
                            
                            execute_query(
                                "INSERT INTO Reservaciones (cliente_id, producto, categoria, precio, abono_total, descripcion, fecha, estado) VALUES (?, ?, ?, ?, ?, ?, ?, 'Pendiente')",
                                (c_id, producto_res, cat_l, precio_res, abono_ini, desc_res, f_act)
                            )
                            if abono_ini == precio_res:
                                execute_query("UPDATE Reservaciones SET estado = 'Completada' WHERE id = (SELECT MAX(id) FROM Reservaciones)")
                                # Obtener ID de la venta recién creada usando el retorno de execute_query
                                v_id_last = execute_query(
                                    "INSERT INTO Ventas (cliente_id, producto, categoria, precio, descripcion, fecha) VALUES (?, ?, ?, ?, ?, ?)",
                                    (c_id, producto_res, cat_l, precio_res, desc_res, f_act)
                                )
                                f_inv = generar_factura(v_id_last, precio_res)
                                
                                st.success("Reserva pagada en su totalidad.")
                                mostrar_factura_ui(v_id_last, cliente_res, producto_res, precio_res, f_inv)
                            else:
                                st.success("Reservación registrada correctamente.")
                            st.cache_data.clear()
                        except Exception as e:
                            st.error(f"Error: {e}")

        with col_res2:
            st.write("#### 💰 Cuentas Pendientes")
            query_pendientes = """
            SELECT r.id, c.nombre || ' - ' || c.telefono as Cliente, r.producto, r.precio, r.abono_total 
            FROM Reservaciones r
            JOIN Clientes c ON r.cliente_id = c.id
            WHERE r.estado = 'Pendiente'
            """
            df_pendientes = fetch_data(query_pendientes)
            
            if df_pendientes.empty:
                st.info("No hay reservaciones pendientes de pago.")
            else:
                opciones_abonos = {
                    f"{row['Cliente']} | {row['producto']} (Resta: ${row['precio'] - row['abono_total']:.2f})": row["id"]
                    for _, row in df_pendientes.iterrows()
                }
                res_sel = st.selectbox("Seleccione Reservación a Abonar:", list(opciones_abonos.keys()))
                
                if res_sel:
                    r_id = opciones_abonos[res_sel]
                    datos_res = fetch_data("SELECT precio, abono_total, cliente_id, producto, categoria, descripcion FROM Reservaciones WHERE id = ?", (r_id,)).iloc[0]
                    saldo_restante = datos_res['precio'] - datos_res['abono_total']
                    
                    with st.form("abonar_form"):
                        st.write(f"**Precio Total:** ${datos_res['precio']:.2f}")
                        st.write(f"**Abonado hasta ahora:** ${datos_res['abono_total']:.2f}")
                        st.write(f"**Saldo Restante:** ${saldo_restante:.2f}")
                        
                        nuevo_abono = st.number_input("Monto a Abonar ($)", min_value=0.1, max_value=float(saldo_restante), value=float(saldo_restante), step=0.1)
                        
                        sub_abonar = st.form_submit_button("Registrar Abono")
                        if sub_abonar:
                            nuevo_total = datos_res['abono_total'] + nuevo_abono
                            try:
                                if nuevo_total >= datos_res['precio']:
                                    # Pasa a Venta Completada
                                    execute_query("UPDATE Reservaciones SET abono_total = ?, estado = 'Completada' WHERE id = ?", (float(nuevo_total), int(r_id)))
                                    # Insertar en Ventas
                                    fecha_venta = date.today().strftime("%Y-%m-%d")
                                    v_id_res = execute_query(
                                        "INSERT INTO Ventas (cliente_id, producto, categoria, precio, descripcion, fecha) VALUES (?, ?, ?, ?, ?, ?)",
                                        (int(datos_res['cliente_id']), str(datos_res['producto']), str(datos_res['categoria']), float(datos_res['precio']), str(datos_res['descripcion']), fecha_venta)
                                    )
                                    f_inv_res = generar_factura(v_id_res, datos_res['precio'])
                                    
                                    st.success("¡Cobro completado!")
                                    mostrar_factura_ui(v_id_res, res_sel.split('|')[0], datos_res['producto'], datos_res['precio'], f_inv_res)
                                else:
                                    execute_query("UPDATE Reservaciones SET abono_total = ? WHERE id = ?", (float(nuevo_total), int(r_id)))
                                    st.success(f"Abono de ${nuevo_abono:.2f} registrado. Nuevo saldo restante: ${datos_res['precio'] - nuevo_total:.2f}")
                                st.cache_data.clear()
                            except Exception as e:
                                st.error(f"Error al procesar: {e}")

with tab2:
    st.write("### 🛒 Registro de Nueva Venta")
    # Cargar clientes (ya está disponible en la variable `clientes_dict`)
    if clientes_df.empty:
        st.warning("⚠️ No hay clientes registrados.")
    else:
        with st.form("registro_venta_form", clear_on_submit=True):
            cliente_seleccionado = st.selectbox("Cliente *", clientes_nombres)
            producto = st.text_input("Producto *")
            categoria = st.selectbox("Categoría *", categorias_disp)
            precio = st.number_input("Precio ($) *", min_value=0.0, value=0.0, step=0.1)
            descripcion = st.text_area("Descripción *")
            
            submitted = st.form_submit_button("Registrar Venta Directa")
            
            if submitted:
                if not producto or not descripcion or precio <= 0:
                    st.error("Todos los campos con * son obligatorios y el precio debe ser mayor a 0.")
                else:
                    try:
                        cliente_id = clientes_dict[cliente_seleccionado]
                        cat_letra = categoria[0]
                        fecha_actual = date.today().strftime("%Y-%m-%d")
                        
                        v_id_directa = execute_query(
                            "INSERT INTO Ventas (cliente_id, producto, categoria, precio, descripcion, fecha) VALUES (?, ?, ?, ?, ?, ?)",
                            (cliente_id, producto, cat_letra, precio, descripcion, fecha_actual)
                        )
                        f_inv_dir = generar_factura(v_id_directa, precio)
                        
                        st.success("Venta directa registrada.")
                        mostrar_factura_ui(v_id_directa, cliente_seleccionado, producto, precio, f_inv_dir)
                        st.cache_data.clear()
                    except Exception as e:
                        st.error(f"Error al registrar la venta: {e}")

with tab3:
    st.write("### 📋 Historial de Ventas")
    query_historial = """
    SELECT c.nombre as Cliente, v.producto as Producto, v.categoria as Categoría, 
           v.precio as Precio, v.descripcion as Descripción, v.fecha as Fecha
    FROM Ventas v
    JOIN Clientes c ON v.cliente_id = c.id
    ORDER BY v.fecha DESC, v.id DESC
    """
    ventas_hi_df = fetch_data(query_historial)
    
    if not ventas_hi_df.empty:
        st.dataframe(ventas_hi_df, use_container_width=True, hide_index=True)
    else:
        st.info("No hay ventas registradas.")

with tab4:
    st.write("### 🗄️ Historial de Facturas y Reimpresión")
    query_facturas = """
    SELECT f.id as 'No. Factura', c.nombre as Cliente, v.producto as Producto, 
           f.monto_total as Total, f.fecha as 'Fecha Emisión', f.tipo as Tipo, f.venta_id
    FROM Facturas f
    JOIN Ventas v ON f.venta_id = v.id
    JOIN Clientes c ON v.cliente_id = c.id
    ORDER BY f.id DESC
    """
    df_facturas = fetch_data(query_facturas)
    
    if df_facturas.empty:
        st.info("No se han emitido facturas aún.")
    else:
        col_f1, col_f2 = st.columns([1, 1])
        with col_f1:
            st.dataframe(df_facturas.drop(columns=['venta_id']), use_container_width=True, hide_index=True)
        
        with col_f2:
            st.write("#### 🔍 Reimpresión / Vista Previa")
            facturas_opciones = {f"Factura #{row['No. Factura']} - {row['Cliente']}": row for _, row in df_facturas.iterrows()}
            fact_sel = st.selectbox("Seleccione Factura:", list(facturas_opciones.keys()))
            
            if fact_sel:
                datos_f = facturas_opciones[fact_sel]
                mostrar_factura_ui(datos_f['venta_id'], datos_f['Cliente'], datos_f['Producto'], datos_f['Total'], datos_f['Fecha Emisión'], datos_f['Tipo'])
                
                col_btn_f1, col_btn_f2 = st.columns(2)
                with col_btn_f1:
                    if st.button("🖨️ Simular Impresión Simple"):
                        st.write("*(Enviando a impresora de recibos...)*")
                with col_btn_f2:
                    if st.button("📧 Re-enviar Factura Digital"):
                        st.write(f"*(Enviando a {datos_f['Cliente']}...)*")
