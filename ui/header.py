import streamlit as st
from streamlit.delta_generator import DeltaGenerator

from Chatbot import chatbot
from tools.tools import all_tools


def header():
    if "example_questions" not in st.session_state:
        st.session_state.example_questions = []

    col1, col2 = st.columns([5, 5])
    with col1:
        st.title(chatbot.fancy_name)
        st.caption(chatbot.description)

    with col2:
        from Actions import ask_question

        st.session_state.example_questions.clear()  # Clear previous entries
        idx = 0

        cols: list[DeltaGenerator] = []
        for tool in all_tools:
            for question in tool.example_questions:
                st.session_state.example_questions.append(
                    {
                        "label": question.label,
                        "prompt": question.prompt,
                        "icon": question.icon if question.icon else "✨",
                    }
                )

                if idx % 3 == 0:  # Create new columns every 2 buttons
                    cols = st.columns(3)

                col_idx = idx % 3  # Alternate between the two columns
                with cols[col_idx]:
                    st.button(
                        label=question.label,
                        on_click=ask_question,
                        args=(question.prompt,),
                        icon=question.icon if question.icon else "✨",
                        use_container_width=True,
                    )
                idx += 1

    st.divider()
