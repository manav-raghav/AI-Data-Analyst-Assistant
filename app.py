import streamlit as st

from src.analysis import (
    get_correlation_matrix,
    get_data_types,
    get_dataset_shape,
    get_duplicate_count,
    get_missing_values,
    get_numeric_summary,
    get_outlier_summary,
)
from src.data_loader import load_data
from src.visualization import create_histogram

st.title("AI Data Analyst Assistant")

st.write("Upload a dataset to get started.")

uploaded_file = st.file_uploader(
    "Choose a CSV, Excel, or JSON file",
    type=["csv", "xlsx", "xls", "json"],
)

if uploaded_file is not None:
    data = load_data(uploaded_file)

    if data is not None:
        rows, columns = get_dataset_shape(data)

        st.success("File loaded successfully!")

        st.header("Dataset Overview")
        st.write(f"Number of rows: {rows}")
        st.write(f"Number of columns: {columns}")
        st.write(f"Number of duplicate rows: {get_duplicate_count(data)}")

        st.header("Dataset Preview")
        st.dataframe(data.head().astype(str))

        st.header("Data Types")
        data_types = get_data_types(data).astype(str).to_frame(name="Data Type")
        st.dataframe(data_types)

        st.header("Missing Values")
        missing_values = get_missing_values(data).to_frame(name="Missing Values")
        st.dataframe(missing_values)

        st.header("Statistical Summary")
        st.dataframe(get_numeric_summary(data))

        st.header("Correlation Matrix")
        correlation_matrix = get_correlation_matrix(data)
        if not correlation_matrix.empty:
            st.dataframe(correlation_matrix)
        else:
            st.info("Correlation analysis requires numerical columns in the dataset.")

        st.header("Potential Outliers")
        outlier_summary = get_outlier_summary(data)
        if not outlier_summary.empty:
            st.dataframe(outlier_summary)
            st.info(
                "These are potential outliers identified using the IQR method. "
                "Investigate them before deciding whether to remove them."
            )
        else:
            st.success("No potential outliers were detected.")

        st.header("Visualizations")
        numerical_columns = data.select_dtypes(include="number").columns.tolist()

        if numerical_columns:
            selected_column = st.selectbox(
                "Choose a numerical column for the histogram",
                numerical_columns,
            )
            histogram = create_histogram(data, selected_column)
            st.pyplot(histogram)
        else:
            st.info("A histogram requires at least one numerical column in the dataset.")
