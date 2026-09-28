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
from src.ai_assistant import get_ai_response
from src.prompt_builder import (
    build_analysis_prompt,
    build_dataset_context,
    build_local_analysis_prompt,
    is_chart_question,
    build_chart_context,
    build_computed_answer_context,
)
from src.visualization import (     
    create_histogram,
    create_bar_chart,
    create_scatter_plot
)

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

        #Histogram
        st.subheader("Histogram")
        selected_column = None

        if numerical_columns:
            selected_column = st.selectbox(
                "Choose a numerical column for the histogram",
                numerical_columns,
            )
            histogram = create_histogram(data, selected_column)
            st.pyplot(histogram)
        else:
            st.info("A histogram requires at least one numerical column in the dataset.")
        
        # Bar Chart
        st.subheader("Bar Chart")

        # Select categorical columns for the bar chart
        categorical_columns = data.select_dtypes(
           include=["object","string", "category", "bool"]
        ).columns.tolist()

        selected_bar_column = None

        if categorical_columns:
            selected_bar_column = st.selectbox(
            "Select a column for the bar chart",
            categorical_columns,
            key="bar_chart_column",
            )
            bar_chart = create_bar_chart(data, selected_bar_column)
            st.pyplot(bar_chart)
        else:
            st.info("No categorical columns are available for a bar chart.")

        
        # Scatter Plot
        st.subheader("Scatter Plot")

        # Get numeric columns
        numeric_columns = data.select_dtypes(include="number").columns.tolist()
        x_column = None
        y_column = None

        if len(numeric_columns) >= 2:
            col1, col2 = st.columns(2)

            with col1:
                x_column = st.selectbox(
                    "Select X-axis column",
                    numeric_columns,
                    key="scatter_x_column",
                )

            with col2:
                # Choose a different default column for the Y-axis
                y_index = 1 if len(numeric_columns) > 1 else 0

                y_column = st.selectbox(
                    "Select Y-axis column",
                    numeric_columns,
                    index=y_index,
                    key="scatter_y_column",
                )

            scatter_plot = create_scatter_plot(
                data,
                x_column,
                y_column,
            )

            st.pyplot(scatter_plot)

        else:
            st.info(
                "At least two numeric columns are required for a scatter plot."
            )

        st.header("Ask AI About Your Dataset")
        user_question = st.text_area(
            "Ask a question about your uploaded dataset",
            placeholder="For example: What are the most important patterns in this dataset?",
        )

        if st.button("Ask AI"):
            if not user_question.strip():
                st.warning("Please enter a question before asking the AI.")
            else:
                dataset_context = build_dataset_context(data)
                prompt = build_analysis_prompt(dataset_context, user_question)
                fallback_prompt = build_local_analysis_prompt(data, user_question)
                computed_context = build_computed_answer_context(
                    data,
                    user_question,
                )

                if computed_context:
                    prompt += f"\n\n{computed_context}"
                    fallback_prompt += f"\n\n{computed_context}"
            
                # Add chart information only for chart-related questions
                if is_chart_question(user_question):
                    chart_context = build_chart_context(
                        data,
                        histogram_column=selected_column,
                        bar_column=selected_bar_column,
                        scatter_x=x_column,
                        scatter_y=y_column,
                    )

                    prompt += f"\n\n{chart_context}"
                    fallback_prompt += f"\n\n{chart_context}"
                ai_response = get_ai_response(prompt, fallback_prompt)

                st.subheader("AI Analysis")
                st.write(ai_response)
