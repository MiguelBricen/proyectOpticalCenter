import streamlit as st
import os
import sys

# Agregar el directorio actual al path para importar módulos correctamente
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import init_db
from utils.ui_components import header_ui
from utils.helpers import login_user, logout, execute_query, fetch_data

# Configuración de la página
st.set_page_config(page_title="Óptica Stefany | Gestión Profesional", page_icon="👓", layout="wide")

# Inicializar base de datos
init_db()

# --- ESTILOS CSS PERSONALIZADOS ---
st.markdown("""
    <style>
    /* Spacing adjustments - Lowering slightly */
    .block-container { padding-top: 2.5rem !important; padding-bottom: 1rem !important; }
    .main { background-color: #f8f9fa; }
    
    /* Logout button style - much more to the right */
    .logout-container {
        text-align: right;
        width: 100%;
        padding-right: 0px;
        margin-top: 5px;
    }
    
    /* ESTILO PARA LAS 6 CARDS PRINCIPALES */
    div.stButton > button[key^="card_"] {
        width: 100% !important;
        height: 180px !important;
        background-color: white !important;
        color: #2c3e50 !important;
        border-radius: 12px !important;
        border: 1px solid #dee2e6 !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05) !important;
        transition: all 0.2s ease !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        align-items: center !important;
        padding: 10px !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        white-space: pre-wrap !important;
    }
    div.stButton > button[key^="card_"]:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 15px rgba(0,0,0,0.1) !important;
        border-color: #007bff !important;
        color: #007bff !important;
    }

    /* ESTILO PARA BOTONES TIPO ETIQUETA/LINK (Logout, Olvido, Volver) */
    div.stButton > button[key$="_link"], div.stButton > button[key="forgot"] {
        background: none !important;
        border: none !important;
        padding: 0 !important;
        color: #007bff !important;
        text-decoration: underline !important;
        font-size: 0.95rem !important;
        font-weight: normal !important;
        box-shadow: none !important;
        height: auto !important;
        width: auto !important;
        display: inline !important;
        background-color: transparent !important;
        float: right !important;
    }
    div.stButton > button[key$="_link"]:hover, div.stButton > button[key="forgot"]:hover {
        color: #0056b3 !important;
        text-decoration: none !important;
        background: none !important;
    }
    
    /* Header adjustments */
    h1 { margin-top: 0px !important; margin-bottom: 0 !important; }
    .stImage { margin-top: 0px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- MANEJO DE SESIÓN / LOGIN ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "login_mode" not in st.session_state:
    st.session_state.login_mode = "login"

if not st.session_state.authenticated:
    col_l1, col_l2, col_l3 = st.columns([1, 1.5, 1])
    with col_l2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        if st.session_state.login_mode == "login":
            st.markdown("<h2 style='text-align: center;'>🔐 Acceso al Sistema</h2>", unsafe_allow_html=True)
            with st.form("login_form"):
                usuario = st.text_input("Usuario")
                clave = st.text_input("Contraseña", type="password")
                if st.form_submit_button("Iniciar Sesión", use_container_width=True):
                    user = login_user(usuario, clave)
                    if user:
                        st.session_state.authenticated = True
                        st.session_state.username = user['usuario']
                        st.session_state.role = user['rol']
                        st.rerun()
                    else: st.error("Fallo.")
            
            # Olvido su contraseña como etiqueta (Independiente)
            if st.button("¿Olvidó su contraseña?", key="forgot"):
                st.session_state.login_mode = "forgot"
                st.rerun()
        else:
            st.markdown("<h3 style='text-align: center;'>🔑 Recuperación</h3>", unsafe_allow_html=True)
            with st.form("recovery_form"):
                user_rec = st.text_input("Usuario")
                master_code = st.text_input("Código Maestro", type="password")
                new_pass = st.text_input("Nueva Contraseña", type="password")
                if st.form_submit_button("Actualizar"):
                    if master_code == "2024":
                        execute_query("UPDATE Usuarios SET clave = ? WHERE usuario = ?", (new_pass, user_rec))
                        st.success("Listo.")
                        st.session_state.login_mode = "login"
                    else: st.error("Error.")
            if st.button("Volver al Login", key="back_link"):
                st.session_state.login_mode = "login"
                st.rerun()
    st.stop()

# --- CABECERA ---
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.markdown("<h1 style='color:#2c3e50;'>👓 Óptica Stefany</h1><p style='color:#666;'>Software de Gestión Profesional</p>", unsafe_allow_html=True)

with col_h2:
    role_icon = "🛡️" if st.session_state.role == "Administrador" else "👤"
    st.markdown(f"<div style='text-align:right; line-height:1.4;'><b>{st.session_state.username}</b><br><span style='font-size:0.85rem; color:#555;'>{role_icon} {st.session_state.role}</span></div>", unsafe_allow_html=True)
    # Logout mucho más a la derecha
    if st.button("Cerrar Sesión", key="logout_top_link"):
        logout()

st.markdown("<hr style='margin: 30px 0;'>", unsafe_allow_html=True)

# --- SECCIÓN PRINCIPAL ---
col_main_img, col_main_info = st.columns([1.5, 2])
with col_main_img:
    image_path = os.path.join("assets", "autorefractor.png")
    if os.path.exists(image_path):
        st.image(image_path, use_container_width=True)
with col_main_info:
    st.markdown(f"""
    ### 📁 Bienvenido de nuevo
    Gestione su óptica con eficiencia y profesionalismo. Acceda a los expedientes de sus pacientes y controle sus ventas.
    
    #### 🚀 Accesos:
    *   **Clientes**: Expedientes detallados y contacto.
    *   **Ventas**: Facturación inmediata, reservaciones y abonos.
    *   **Inventario**: Monitoreo dinámico de productos.
    *   **Administración**: Gestión de personal y reportes integrados.
    """, unsafe_allow_html=True)

st.markdown("<br> 🛠️ Panel de Control", unsafe_allow_html=True)

# --- PANEL DE CONTROL (6 CARDS) ---
c1, c2, c3 = st.columns(3)
with c1:
    if st.button("👥 CLIENTES\nPacientes y expedientes", key="card_c1"): st.switch_page("pages/01_Clientes.py")
with c2:
    if st.button("💸 VENTAS\nFacturas y abonos", key="card_c2"): st.switch_page("pages/02_Ventas.py")
with c3:
    if st.button("📦 INVENTARIO\nControl de productos", key="card_c3"): st.switch_page("pages/03_Inventario.py")

c4, c5, c6 = st.columns(3)
with c4:
    if st.session_state.role == "Administrador":
        if st.button("👷 PERSONAL\nPlanilla y horarios", key="card_c4"): st.switch_page("pages/04_Trabajadores.py")
    else: st.button("🔒 PERSONAL\nAcceso restringido", disabled=True, key="card_c4_lock")
with c5:
    if st.session_state.role == "Administrador":
        if st.button("📊 REPORTES\nEstadísticas y KPIs", key="card_c5"): st.switch_page("pages/05_Reportes.py")
    else: st.button("🔒 REPORTES\nAcceso restringido", disabled=True, key="card_c5_lock")
with c6:
    st.button("🔔 PRÓXIMAMENTE\nMás herramientas", disabled=True, key="card_c6_next")

# SIDEBAR
st.sidebar.markdown(f"### 📱 Estado")
st.sidebar.success(f"Usuario: **{st.session_state.username}**")
st.sidebar.info(f"Rol: **{st.session_state.role}**")

st.markdown("<br><hr>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #999; font-size: 0.8rem;'>© 2024 Óptica Stefany</p>", unsafe_allow_html=True)

