import streamlit as st


def styles():
    st.markdown(
        """
        <style>
            h1 {
                padding-top: 0 !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
