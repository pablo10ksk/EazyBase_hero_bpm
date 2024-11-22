import requests
import streamlit as st
from pandas import DataFrame
from pandasai import SmartDataframe
from pandasai.llm import OpenAI

from Api import get_endpoint
from tools.XyzTool import XyzTool


class PendingTasksPandasAITool(XyzTool):
    def __init__(self):
        super().__init__(
            name="questions_over_tasks",
            description="Use this to answer questions about tasks",
            human_name="Questions over tasks",
            human_description="Use this to answer questions about tasks",
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
        llm = OpenAI()
        df = SmartDataframe(tasks, config={"llm": llm})  # type: ignore
        return {
            "answer": df.chat(prompt),
        }

    def text(self, data: dict) -> str:
        return ""

    def render(self, text: str, payload: dict) -> None:
        res = payload["answer"]
        if isinstance(res, DataFrame):
            st.dataframe(res)
            return
        if not isinstance(res, str):
            st.markdown(str(res))
            return
        assert isinstance(res, str)
        # This is a url, so render it
        if "uXYZ_bpm" in res:
            st.image(res)
            return
        st.markdown(res)
        return
