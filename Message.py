from dataclasses import dataclass
from typing import Literal, Optional
from uuid import uuid4

import streamlit as st

from tools.tools import all_tools


@dataclass(init=False)
class Message:
    message_id: str
    text: str
    role: Literal["user", "assistant", "system"]

    # This is used when a question is made but we don't
    # really want to show its internal representation
    shallow_text: Optional[str] = None
    tool_type: Optional[str] = None
    payload: Optional[dict] = None

    def __init__(
        self,
        text: str,
        role: Literal["user", "assistant", "system"],
        shallow_text: Optional[str] = None,
        tool_type: Optional[str] = None,
        payload: Optional[dict] = None,
    ):
        self.message_id = str(uuid4())

        self.text = text
        self.role = role
        self.shallow_text = shallow_text
        self.tool_type = tool_type
        self.payload = payload

    def render(self):
        try:
            if self.tool_type:
                self._render_tool()
            else:
                self._render_text()
        except Exception as e:
            st.error(f"Error: {e}")

    def _render_text(self):
        if self.shallow_text:
            st.markdown(f"_{self.shallow_text}_")
        else:
            st.markdown(self.text)

    def _render_tool(self):
        for tool in all_tools:
            if tool.name == self.tool_type:
                tool.message_id = self.message_id
                tool.render(self.text, self.payload)
                break
