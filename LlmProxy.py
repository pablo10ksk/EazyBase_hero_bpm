from dataclasses import dataclass
from json import loads
from typing import Optional, Tuple
from uuid import uuid4

import requests
import streamlit as st
from openai import OpenAI

from Agent import Agent
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

    MODEL = "gpt-4o-mini"

    def __init__(self, login: Login):
        self.client = OpenAI()
        self.historial = Historial()
        self.login = login
        self.eazybase = EazyBase(login)

    def route_prompt(self):
        last_message = self.historial.get_last_message()
        assert last_message is not None, "No messages in the historial"
        prompt = last_message.text
        agent: Agent = st.session_state.agent
        return agent.route_prompt(
            prompt,
            all_tools,
            self.historial.get_last_messages_except_last(),
        )

    def run_tool(self, tool: Optional[XyzTool], input: dict | str):
        new_id = str(uuid4())
        last_message = self.historial.get_last_message()
        assert last_message is not None, "No messages in the historial"
        prompt = last_message.text
        if tool:
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
        else:
            return Message(text=str(input), role="assistant")

    def is_logged_in(self) -> bool:
        return self.login.is_logged_in()

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
            response_format={"type": "json_object"},
        )
        return response.choices[0].message.content

    def add_message(self, m):
        self.historial.add_message(m)
