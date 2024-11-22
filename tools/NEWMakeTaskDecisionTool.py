import requests
from pydantic import BaseModel

from Api import get_endpoint
from tools.SimpleXyzTool import SimpleXyzTool


class MakeTaskDecisionInput(BaseModel):
    task_id: str
    option_code: str
    # comment: str | None


class NEWMakeTaskDecisionTool(SimpleXyzTool):
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
        url = get_endpoint("MakeDecision")
        payload = {
            "token": self.global_payload.token,
            "ejecTareaId": self.input.task_id,
            "opcionCd": self.input.option_code,
        }
        headers = {"Content-Type": "application/json"}

        response = requests.get(url, headers=headers, json=payload)
        return {
            "ok": response.ok,
            "data": response.json(),
        }

    def text(self, data: dict) -> str:
        if data["ok"]:
            return "The decision was made successfully."
        else:
            message = data["data"]["message"]
            return f"An error occurred: {message}"
