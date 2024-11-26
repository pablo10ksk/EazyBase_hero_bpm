import streamlit as st
from pydantic import BaseModel

from tools.SimpleXyzTool import SimpleXyzTool


class MakeTaskDecisionInput(BaseModel):
    task_id: str
    option_code: str
    # comment: str | None


class MakeTaskDecisionTool(SimpleXyzTool):
    input: MakeTaskDecisionInput

    def __init__(self):
        super().__init__(
            name="task_decision",
            description="BPMs are stuck in human decision tasks until a decision is made. This tool, given a task Id and a decision code, will make the decision on the task. If the user wants to _know_ the decisions for a task (not really taking an action), display for them the task instead.",
            human_name="Tomar una decisión",
            human_description="Toma una decisión sobre una tarea.",
            schema=MakeTaskDecisionInput,
        )

    def run(self, prompt: str) -> dict:
        return st.session_state.api.make_decision(
            task_id=self.input.task_id,
            option_code=self.input.option_code,
        )

    def text(self, data: dict) -> str:
        if data["ok"]:
            return "The decision was made successfully."
        else:
            message = data["data"]["message"]
            return f"An error occurred: {message}"
