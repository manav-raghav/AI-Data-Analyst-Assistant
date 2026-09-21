"""Helpers for loading files uploaded through Streamlit."""

import pandas as pd
import streamlit as st


def load_data(uploaded_file):
    """Load a CSV or Excel or JSON upload into a Pandas DataFrame.

    Returns ``None`` when the file cannot be loaded, after showing a helpful
    message in the Streamlit app.
    """
    if uploaded_file is None:
        return None

    file_name = uploaded_file.name.lower()

    try:
        if file_name.endswith(".csv"):
            return pd.read_csv(uploaded_file)

        if file_name.endswith((".xlsx", ".xls")):
            return pd.read_excel(uploaded_file)
        if file_name.endswith(".json"):
            return pd.read_json(uploaded_file)

        st.error("Please upload a CSV (.csv) or Excel (.xlsx, .xls) or JSON (.json) file.")
        return None

    except pd.errors.EmptyDataError:
        st.error("This file is empty. Please upload a file that contains data.")
    except pd.errors.ParserError:
        st.error("Please upload a CSV (.csv), Excel (.xlsx, .xls), or JSON (.json) file.")
    except (ImportError, ValueError) as error:
        st.error(f"I could not load this file: {error}")
    except Exception as error:
        st.error(f"An unexpected error occurred while loading the file: {error}")

    return None
