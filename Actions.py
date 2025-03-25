import streamlit as st

from LlmProxy import LlmProxy
from Message import Message


def ask_shallow_question(shallow_prompt: str, prompt: str) -> None:
    """
    Asks a question where the _real_ question (i.e., the one that the LLM gets) and what the user sees are different.

    :param shallow_prompt: The prompt that the user sees.
    :param prompt: The prompt that the
    """
    user_message = Message(text=prompt, role="user")
    user_message.shallow_text = shallow_prompt
    st.session_state.client.add_message(user_message)
    with st.session_state.ui_questions:
        with st.chat_message("user"):
            user_message.render()

    answer()


def ask_question(prompt: str) -> None:
    """
    Asks a question

    :param prompt: The prompt to ask
    """
    user_message = Message(text=prompt, role="user")
    st.session_state.client.add_message(user_message)
    with st.session_state.ui_questions:
        with st.chat_message("user"):
            user_message.render()

    answer()


def answer() -> None:
    """
    Answers the last question
    """
    with st.session_state.ui_questions:
        with st.chat_message("assistant"):
            assistant_message = get_answer()
            assistant_message.render()
            st.session_state.client.historial.add_message(assistant_message)

 
def get_answer() -> Message:
    """
    Retrieves an answer from the chatbot based on the user's input.

    Returns:
        Message: The response message from the chatbot.
    """
    client: LlmProxy = st.session_state.client
    with st.spinner("Validando credenciales..."):
        if not client.is_logged_in():
            return Message(
                text="Debes iniciar sesión antes de usar este chatbot.",
                role="assistant",
            )

    with st.spinner("Estudiando lo que me has pedido..."):
        tool, input = client.route_prompt()

    last_spinner_text = (
        f"Veo que quieres '{tool.human_name}'. Voy a revisar la documentación y a decidir cómo contestarte. Permíteme unos instantes..."
        if tool is not None
        else "Ya entiendo. Un instante y te contesto..."
    )
    with st.spinner(last_spinner_text):
        return client.run_tool(tool, input)
