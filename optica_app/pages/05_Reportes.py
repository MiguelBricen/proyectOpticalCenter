import streamlit as st
import plotly.express as px
import pandas as pd
from utils.helpers import fetch_data, check_auth
from utils.ui_components import header_ui

# Verificación de Autenticación y Rol
if not check_auth():
    st.warning("⚠️ Acceso denegado. Por favor, inicie sesión en la página principal.")
    st.stop()

if st.session_state.role != "Administrador":
    st.error("🚫 No tiene permisos para acceder a esta sección.")
    st.stop()

st.set_page_config(page_title="Reportes | Óptica Stefany", page_icon="📊", layout="wide")
header_ui("Reportes y Dashboards", "Indicadores clave de rendimiento (KPIs)")

# Cargar datos
df_ventas = fetch_data("SELECT * FROM Ventas")
df_horas = fetch_data("""
    SELECT t.nombre, SUM(h.horas) as total_horas 
    FROM Horas_trabajo h
    JOIN Trabajadores t ON h.trabajador_id = t.id
    GROUP BY t.nombre
""")

if df_ventas.empty:
    st.warning("No hay suficientes datos de ventas para generar reportes.")
else:
    # KPIs
    st.write("### Indicadores Principales")
    total_ingresos = df_ventas["precio"].sum()
    ventas_totales = len(df_ventas)
    ticket_promedio = total_ingresos / ventas_totales if ventas_totales > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Ingresos Totales", f"${total_ingresos:,.2f}")
    col2.metric("Nº de Ventas", f"{ventas_totales}")
    col3.metric("Ticket Promedio", f"${ticket_promedio:,.2f}")
    
    st.markdown("---")
    
    # Gráficos de Ventas
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.write("#### Ingresos por Categoría")
        ventas_por_categoria = df_ventas.groupby("categoria")["precio"].sum().reset_index()
        # Usamos una paleta de colores vibrantes y distintos
        fig_cat = px.pie(ventas_por_categoria, names="categoria", values="precio", 
                         title="Distribución de Ingresos por Categoría",
                         color_discrete_sequence=px.colors.qualitative.Plotly)
        st.plotly_chart(fig_cat, use_container_width=True)
        
    with col_chart2:
        st.write("#### Top Productos Vendidos")
        ventas_por_pro = df_ventas.groupby("producto").size().reset_index(name='cantidad_vendida')
        ventas_por_pro = ventas_por_pro.sort_values('cantidad_vendida', ascending=False).head(10)
        fig_top = px.bar(ventas_por_pro, x="producto", y="cantidad_vendida", 
                         title="Productos Más Vendidos (Top 10)",
                         labels={"producto": "Producto", "cantidad_vendida": "Cantidad"},
                         color="producto", color_discrete_sequence=px.colors.qualitative.Vivid)
        st.plotly_chart(fig_top, use_container_width=True)

st.markdown("---")
st.write("### Control de Horas del Personal")
if not df_horas.empty:
    fig_horas = px.bar(df_horas, x="nombre", y="total_horas", 
                       title="Total de Horas por Trabajador",
                       labels={"nombre": "Trabajador", "total_horas": "Horas Totales"},
                       color="total_horas", color_continuous_scale="Blues")
    st.plotly_chart(fig_horas, use_container_width=True)
else:
    st.info("No hay registros de horas de trabajadores para mostrar.")
