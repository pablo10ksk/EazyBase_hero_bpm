from dataclasses import dataclass
from json import loads
from typing import Optional, Tuple
from uuid import uuid4

from openai import OpenAI

from EazyBase import EazyBase
from Historial import Historial
from Login import Login
from Message import Message
from tools.tools import all_tools
from tools.XyzTool import XyzTool


@dataclass
class LlmProxy:
    client: OpenAI
    historial: Historial
    login: Login

    LIGHT_MODEL = "gpt-4o-mini"
    MODEL = "gpt-4o-mini"

    def __init__(self, login: Login):
        self.client = OpenAI()
        self.historial = Historial()
        self.login = login
        self.eazybase = EazyBase(login)

    def answer_last_message(self) -> Message:
        new_id = str(uuid4())

        if not self.login.is_logged_in():
            return Message(
                text="Debes iniciar sesión antes de usar este chatbot.",
                role="assistant",
            )

        last_message = self.historial.get_last_message()
        if not last_message:
            return Message(
                text="No tengo nada a que responder.",
                role="assistant",
            )
        prompt = last_message.text
        tool, input = self.route_prompt(prompt)

        if tool:
            tool.global_payload = self.login.global_payload
            tool.message_id = new_id
            tool.set_input(input)
            payload = tool.run(prompt)
            text = tool.text(payload)

            return Message(
                text=text,
                role="assistant",
                tool_type=tool.name,
                payload=payload,
            )

            # Llamar aquí eazy base con
            # usuario: last_message.text,
            # respuesta: text, payload

        else:
            if text := self.regular_call():
                return Message(text=text, role="assistant")
            else:
                return Message(
                    text="Tengo problemas para completar tu solicitud.",
                    role="assistant",
                )

    def regular_call(self) -> Optional[str]:
        response = self.client.chat.completions.create(
            temperature=0,
            model=self.MODEL,
            messages=[
                {
                    "role": m.role,
                    "content": m.text,
                }
                for m in self.historial.get_last_messages()
            ],  # type: ignore
        )
        return response.choices[0].message.content

    def regular_call_with_prompt_without_history(self, prompt: str) -> Optional[str]:
        response = self.client.chat.completions.create(
            temperature=0,
            model=self.MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )
        return response.choices[0].message.content

    def route_prompt(self, prompt: str) -> Tuple[Optional[XyzTool], dict]:
        tasks_description = ""
        for tool in all_tools:
            name = tool.name
            description = tool.description.strip()
            schema = tool.get_input_schema_description()
            tasks_description += f"- *{name}*: {description} | {schema}\n"

        content = f"""
        The user has asked the following:
        -----------------------
        {prompt}
        -----------------------

        You, as an assistant, have access to these tools:

        {tasks_description}
        
        The user will likely ask in Spanish, but you must use the tools with their names as presented above.\n"
        
        You must answer using json:
        - If the goal of a tool matches with the user intent, return {{'tool': '<tool_name>'}} plus the required fields. All the fields are required except those marked with None.
        - If the user makes a general question (not related to the chatbot) or wants you to explain what you have talked so far, return {{}}. 

        Do NOT wrap within ```json tags. Go!
        """

        current_message = {"role": "assistant", "content": content}
        response = self.client.chat.completions.create(
            temperature=0,
            model=self.LIGHT_MODEL,
            messages=[
                *[
                    {
                        "role": m.role,
                        "content": m.text,
                    }
                    for m in self.historial.get_last_messages()
                ],
                current_message,
            ],  # type: ignore
            # response_format={"type": "json_object"},
        )
        response_text = response.choices[0].message.content
        try:
            if response_text:
                response_json = loads(response_text)
                print(response_json)
                tool_name = response_json.get("tool")
                for tool in all_tools:
                    if tool.name == tool_name:
                        return tool, response_json
        except:
            pass
        return None, {}

    def add_message(self, m):
        self.historial.add_message(m)
