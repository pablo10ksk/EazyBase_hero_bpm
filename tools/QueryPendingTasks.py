import requests
import streamlit as st
from pandas import DataFrame
from pandasai import SmartDataframe
from pandasai.llm import OpenAI

from Api import get_endpoint
from tools.ExampleQuestion import ExampleQuestion
from tools.XyzTool import XyzTool


class QueryPendingTasksTool(XyzTool):
    def __init__(self):
        super().__init__(
            name="query_pending_tasks",
            description="Most of the times, users just want to get all the pending tasks. However, sometimes they may want to filter them (e.g., give me the pending tasks until may 2024, which are the last 20 tasks, which task has the ..., etc). For those cases, use this task. This uses PandasAI internally, so USE THIS when the user ask about data frames, strings, numbers, or graphs (histograms, plots,... !).",
            human_name="Responder preguntas sobre tareas pendientes",
            human_description="Permite filtrar, agregar y mostrar gráficos sobre las tareas pendientes.",
            example_questions=[
                ExampleQuestion(
                    label="Gráfico de tareas",
                    prompt="Haz un histograma de la frecuencia de tareas por mes.",
                    icon="📊",
                )
            ],
        )

    def run(self, prompt: str) -> dict:
        url = get_endpoint("GetPendingTasks")
        payload = {
            "token": self.global_payload.token,
            "userId": self.global_payload.userId,
            "userTasksFl": "true",
            "groupsTasksFl": "true",
            "pendingTaskId": "",
            "locatorDs": "",
        }
        headers = {"Content-Type": "application/json"}

        response = requests.get(url, headers=headers, json=payload)
        tasks = response.json()
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
