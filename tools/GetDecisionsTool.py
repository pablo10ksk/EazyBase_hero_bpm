import requests
import streamlit as st
from pydantic import BaseModel

from Api import get_endpoint
from tools.SimpleXyzTool import SimpleXyzTool


class GetDecisionsInput(BaseModel):
    task_id: str


class GetDecisionsTool(SimpleXyzTool):
    input: GetDecisionsInput

    def __init__(self):
        super().__init__(
            name="get_decisions",
            description="BPMs are stuck in human decision tasks until a decision is made. This tool, given a task id, displays which are the possible decisions that can be made on the task.",
            human_name="Get decisions for a task",
            human_description="Displays the possible decisions that can be made on a human task.",
            schema=GetDecisionsInput,
        )

    def run(self, prompt: str) -> dict:
        url = get_endpoint("GetTaskOptionsAdvance")
        payload = {
            "token": self.global_payload.token,
            "taskExecId": self.input.task_id,
        }
        headers = {"Content-Type": "application/json"}

        response = requests.get(url, headers=headers, json=payload)
        res_obj = response.json()
        return {
            "res": res_obj,
        }

    def text(self, data: dict) -> str:
        return str(data)

    def render(self, text: str, payload: dict) -> None:
        res = payload["res"]
        for decision in res:
            title = decision["optionDs"]
            description = decision["optionComments"].strip()
            col1, col2 = st.columns([3, 2])
            id = decision["optionCd"]

            with col1.expander(f"**{title}**"):
                if description:
                    st.caption(f"_{description.strip()}_")
                reasignable = decision["reassignFl"] == 1
                transferable = decision["transferFl"] == 1
                si_no = lambda x: "Sí" if x else "No"
                st.markdown(
                    f"**Reassignable**: {si_no(reasignable)} | **Transferable**: {si_no(transferable)}"
                )

            with col2:
                from Actions import ask_shallow_question

                # TODO: call the MakeTaskDecisionTool
                st.button(
                    "Take action",
                    key=f"{self.message_id}@take_action_{id}",
                    type="primary",
                    use_container_width=True,
                    icon=":material/start:",
                    on_click=lambda in_title, in_id, in_opt: ask_shallow_question(
                        prompt=f"Run the make task decision tool with parameters: task_id = '{in_id}' and option_code = '{in_opt}'",
                        shallow_prompt=f"Toma la decisión {in_title} para la tarea {in_id}",
                    ),
                    args=(title, self.input.task_id, id),
                )
