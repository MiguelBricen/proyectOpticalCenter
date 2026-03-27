import streamlit as st

def header_ui(title, subtitle=None):
    st.title(title)
    if subtitle:
        st.subheader(subtitle)
    st.markdown("---")
