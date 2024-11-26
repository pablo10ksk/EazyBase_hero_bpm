import dotenv
import streamlit as st

from Api import Api
from Chatbot import chatbot
from LlmProxy import LlmProxy
from Login import Login
from ui.header import header
from ui.sidebar import sidebar
from ui.styles import styles

dotenv.load_dotenv()

st.set_page_config(
    page_title=chatbot.title_name,
    layout="wide",
)
styles()

header()

if "client" not in st.session_state:
    st.session_state.login = Login()
    st.session_state.client = LlmProxy(login=st.session_state.login)
    st.session_state.api = Api(login=st.session_state.login)

sidebar()

if "ui_initial" not in st.session_state:
    ui_initial = st.container()
    st.session_state.ui_initial = ui_initial

for message in st.session_state.client.historial._messages:
    with st.chat_message(message.role):
        message.render()

from Actions import ask_question

ui_questions = st.container()
st.session_state.ui_questions = ui_questions

if prompt := st.chat_input("Envía un mensaje...", key="chat_input"):
    ask_question(prompt)
