import streamlit as st


def grid(d: dict, n=3):
    # Display: "key: value" for every key/value pair in d,
    # but distribute them in n columns.
    keys = list(d.keys())
    values = list(d.values())
    for i in range(0, len(keys), n):
        cols = st.columns(n)
        for j, col in enumerate(cols):
            if i + j < len(keys):
                col.markdown(f"**{keys[i+j]}**: {values[i+j]}")
