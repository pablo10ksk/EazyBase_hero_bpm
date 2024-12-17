import streamlit as st

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
            with st.spinner("Validando credenciales...."):
                credentials = st.session_state.client.answer_last_message()
            with st.spinner("Estudiando lo que me has pedido...."):
                tool, input = st.session_state.client.route_prompt()
            if hasattr(tool, "human_name"):
                with st.spinner(
                    f"Veo que quieres '{tool.human_name}', voy a revisar cómo contestarte. Voy a revisar la documentación, permíteme unos instantes"
                ):
                    assistant_message = st.session_state.client.run_tool(tool, input)
            else:
                with st.spinner("Ya entiendo, un instante y te contesto...."):
                    assistant_message = st.session_state.client.run_tool(tool, input)
            assistant_message.render()
            st.session_state.client.historial.add_message(assistant_message)
