import streamlit as st
from streamlit.delta_generator import DeltaGenerator

from Chatbot import chatbot
from tools.tools import all_tools


def header():
    col1, col2 = st.columns([6, 5])
    with col1:
        st.title(chatbot.fancy_name)
        st.caption(chatbot.description)

    with col2:
        from Actions import ask_question

        idx = 0

        cols: list[DeltaGenerator] = []
        for _, tool in enumerate(all_tools):
            for _, question in enumerate(tool.example_questions):
                if idx % 2 == 0:  # Create new columns every 2 buttons
                    cols = st.columns(2)

                col_idx = idx % 2  # Alternate between the two columns
                with cols[col_idx]:
                    st.button(
                        label=question.label,
                        on_click=ask_question,
                        args=(question.prompt,),
                        key=f"example_question_{idx}",
                        icon=question.icon if question.icon else "✨",
                        use_container_width=True,
                    )
                idx += 1

    st.divider()
