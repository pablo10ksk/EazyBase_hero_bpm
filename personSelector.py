from typing import Any

import requests
import streamlit as st
from streamlit_searchbox import st_searchbox

from Api import get_endpoint


def search_name(input: str) -> list[tuple[str, Any]]:
    if input.strip() == "":
        return []
    url = get_endpoint("getUserReassignTask")
    payload = {
        "token": st.session_state.login.get_token(),
        "filterDs": input,
    }
    headers = {"Content-Type": "application/json"}
    response = requests.get(url, headers=headers, json=payload).json()
    try:
        options = []
        for usr in response["USR"]:
            options.append((usr["fullname"], usr))
        for grp in response["GRP"]:
            options.append((grp["grpName"], grp))
        return options
    except Exception as e:
        return []


def autocomplete(key: str = "persons_searcher", label: str = "Transferir a..."):
    st.text(label)
    selected_name = st_searchbox(
        search_name,
        placeholder="Buscar grupo, organización y usuario...",
        key=key,
    )
    # st.write(f"Selected value: {selected_name}")
    return selected_name
