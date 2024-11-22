import streamlit as st


def sidebar():
    """
    The sidebar of the streamlit app
    """
    with st.sidebar:
        login_form()
        st.button(
            "Limpiar chat",
            on_click=lambda: st.session_state.clear(),
            use_container_width=True,
            icon="🗑️",
        )


def login_form():
    login = st.session_state.login
    with st.form("my_login", border=False):
        with st.expander(icon="🔒", label="Sesión", expanded=True):
            email = st.text_input("Usuario")
            password = st.text_input("Contraseña", type="password")
            if st.form_submit_button("Iniciar sesión", icon=":material/login:"):
                login.login(email, password)
                if login.is_logged_in():
                    st.success(
                        "Has iniciado sesión",
                        icon=":material/check:",
                    )
                else:
                    st.error(
                        "No se pudo iniciar sesión",
                        icon=":material/close:",
                    )
