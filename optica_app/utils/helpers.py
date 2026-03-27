import sqlite3
import pandas as pd
import sys
import os
import streamlit as st

# Asegurarnos de poder acceder al subnivel correcto para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_connection

@st.cache_data(ttl=60)
def fetch_data(query, params=()):
    conn = get_connection()
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

def execute_query(query, params=()):
    conn = get_connection()
    c = conn.cursor()
    last_id = None
    try:
        c.execute(query, params)
        last_id = c.lastrowid
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()
    return last_id

def login_user(usuario, clave):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT usuario, rol FROM Usuarios WHERE usuario = ? AND clave = ?", (usuario, clave))
    user = c.fetchone()
    conn.close()
    return user

def check_auth():
    if "authenticated" not in st.session_state or not st.session_state.authenticated:
        return False
    return True

def logout():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()
