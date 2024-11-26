import streamlit as st
from pandas import DataFrame
from pandasai import SmartDataframe
from pandasai.llm import OpenAI

from tools.ExampleQuestion import ExampleQuestion
from tools.XyzTool import XyzTool


class GraphPendingTasksTool(XyzTool):
    def __init__(self):
        super().__init__(
            name="graph_pending_tasks",
            description="Use this tool when the user wants to plot something about the pending tasks.",
            human_name="Gráfico de tareas pendientes",
            human_description="Permite hacer gráficos que dependen de las tareas pendientes",
            example_questions=[
                ExampleQuestion(
                    label="Gráfico de tareas",
                    prompt="Haz un histograma de la frecuencia de tareas por mes.",
                    icon="📊",
                )
            ],
        )

    def run(self, prompt: str) -> dict:
        tasks = st.session_state.api.get_pending_tasks()
        llm = OpenAI(temperature=0)
        df = SmartDataframe(
            tasks,
            config={
                "llm": llm,
                "open_charts": False,
                "save_logs": False,
                "enable_cache": False,
            },  # type:ignore
        )

        try:
            answer = df.chat(prompt)
        except:
            answer = "No se ha podido responder a la pregunta. Por favor, intenta formularla de otra manera."

        isString = isinstance(answer, str)
        return {
            "answer": answer,
            "isText": isString,
            "isGraph": isString and ".png" in answer,
        }

    def text(self, data: dict) -> str:
        if data["isText"] and not data["isGraph"]:
            return data["answer"]
        else:
            return ""

    def render(self, text: str, payload: dict) -> None:
        if payload["isText"] and not payload["isGraph"]:
            st.markdown(text)

        res = payload["answer"]
        if isinstance(res, DataFrame):
            st.dataframe(res)
            return
        if isinstance(res, int):
            st.metric(label="Answer", value=res)
            return
        if not isinstance(res, str):
            st.markdown(str(res))
            return
        assert isinstance(res, str)
        # This is a graph, so we render it
        if payload["isGraph"]:
            st.image(res)
            return
        return
