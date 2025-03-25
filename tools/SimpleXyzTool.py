from typing import Optional

import streamlit as st

from tools.XyzTool import XyzTool


class SimpleXyzTool(XyzTool):
    def render(self, text: str, payload: Optional[dict]) -> None:
        st.markdown(text)
