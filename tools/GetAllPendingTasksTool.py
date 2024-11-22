import os
from uuid import uuid4

import requests
import streamlit as st

from Api import get_endpoint
from tools.ExampleQuestion import ExampleQuestion
from tools.XyzTool import XyzTool


class GetAllPendingTasksTool(XyzTool):
    def __init__(self):
        super().__init__(
            name="get_all_pending_tasks",
            description="Gets all pending tasks for the current user.",
            human_name="Pending tasks",
            human_description="Displays a list of all pending tasks",
            example_questions=[
                ExampleQuestion(
                    "Which are my pending tasks?",
                    "Pending tasks?",
                ),
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
        res_obj = response.json()
        return {
            "tasks": res_obj,
        }

    def text(self, data: dict) -> str:
        n = len(data["tasks"])
        match n:
            case 0:
                return "There are no pending tasks."
            case 1:
                return "There is 1 pending task: \n"
            case _:
                return f"There are {n} pending tasks: \n"

    def render(self, text: str, payload: dict) -> None:
        external_link_url = os.getenv("EXTERNAL_LINK_URL")
        assert external_link_url is not None, "EXTERNAL_LINK_URL is not set"

        st.markdown(text)

        # Iterate through all tasks;
        for task in payload["tasks"]:
            col1, col2 = st.columns([4, 1])
            id = task["EJECUCION_TAREA_ID"]
            name = task["TAREA_DS"]
            link = external_link_url + task["EXTERNAL_LINK_DS"]

            with col1:
                st.markdown(f"[{name}]({link})")
            with col2:

                def ask_for_task():
                    question = f"Can you tell me more about task {id}?"
                    st.info(question)

                uuid = uuid4()
                st.button(
                    key=f"{uuid}@{self.message_id}@prompt_view_task_{id}",
                    label="View task",
                    on_click=ask_for_task,
                )
