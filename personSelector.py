from typing import Any

import streamlit as st
from streamlit_searchbox import st_searchbox


def search_name(input: str) -> list[tuple[str, Any]]:
    reassign_names = st.session_state.api.get_reassign_names(input)
    try:
        options = []
        for usr in reassign_names["USR"]:
            options.append((usr["fullname"], usr))
        for grp in reassign_names["GRP"]:
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
