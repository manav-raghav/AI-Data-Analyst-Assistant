"""Build concise dataset context for the AI Data Analyst Assistant."""

import pandas as pd
import re

from src.analysis import (
    get_correlation_matrix,
    get_data_types,
    get_dataset_shape,
    get_duplicate_count,
    get_missing_values,
    get_numeric_summary,
    get_outlier_summary,
)


def build_dataset_context(df: pd.DataFrame) -> str:
    """Return a structured text summary of a dataset for a future AI prompt."""
    rows, columns = get_dataset_shape(df)
    data_types = get_data_types(df)
    missing_values = get_missing_values(df)
    duplicate_count = get_duplicate_count(df)
    numeric_summary = get_numeric_summary(df)
    correlation_matrix = get_correlation_matrix(df)
    outlier_summary = get_outlier_summary(df)
    sample_data = df.head(5)

    context_parts = [
        "Dataset Overview",
        f"Rows: {rows}\nColumns: {columns}",
        "Columns and Data Types",
        f"Column Names: {', '.join(map(str, df.columns))}\n\n{data_types.to_string()}",
        "Missing Values",
        missing_values.to_string(),
        "Duplicate Rows",
        str(duplicate_count),
        "Statistical Summary",
        numeric_summary.to_string(),
        "Correlations",
        correlation_matrix.to_string(),
        "Potential Outliers",
        outlier_summary.to_string(index=False),
        "Sample Data",
        sample_data.to_string(index=False),
    ]

    return "\n\n".join(context_parts)


def is_chart_question(user_question: str) -> bool:
    """Check whether the user's question is about a chart or plot."""
    if not isinstance(user_question, str):
        return False

    chart_keywords = [
        "chart",
        "plot",
        "graph",
        "histogram",
        "scatter",
        "bar chart",
        "visualization",
        "visualisation",
    ]

    pattern = r"\b(?:" + "|".join(
        re.escape(keyword) for keyword in chart_keywords
    ) + r")\b"

    return bool(re.search(pattern, user_question, flags=re.IGNORECASE))


def build_chart_context(
    df: pd.DataFrame,
    histogram_column: None,
    bar_column: None,
    scatter_x: None,
    scatter_y: None,
):
    """Build context for all three visualizations."""

    context_parts = ["CHART INFORMATION"]

    # 1. Histogram context
    if (
        histogram_column is not None
        and histogram_column in df.columns
        and pd.api.types.is_numeric_dtype(df[histogram_column])
    ):
        histogram_data = df[histogram_column].dropna()

        context_parts.append(
            f"""HISTOGRAM
Column: {histogram_column}
Valid values: {len(histogram_data)}
Statistics:
{histogram_data.describe().to_string()}"""
        )

    # 2. Bar chart context
    if( 
        bar_column is not None
        and bar_column in df.columns
    ):
        counts = (
            df[bar_column]
            .dropna()
            .astype(str)
            .str.strip()
            .str.title()
            .value_counts()
        )

        top_counts = counts.head(10)
        other_count = counts.iloc[10:].sum()

        bar_information = top_counts.to_string()

        if len(counts) > 10:
            bar_information += f"\nOther: {other_count}"

        context_parts.append(
            f"""BAR CHART
Column: {bar_column}
Category counts:
{bar_information}"""
        )

    # 3. Scatter plot context
    if (
        scatter_x is not None
        and scatter_y is not None
        and scatter_x in df.columns
        and scatter_y in df.columns
        and pd.api.types.is_numeric_dtype(df[scatter_x])
        and pd.api.types.is_numeric_dtype(df[scatter_y])
    ):
        plot_data = df[[scatter_x, scatter_y]].dropna()

        if not plot_data.empty:
            correlation = plot_data[scatter_x].corr(
                plot_data[scatter_y]
            )

            context_parts.append(
                f"""SCATTER PLOT
X-axis: {scatter_x}
Y-axis: {scatter_y}
Valid data points: {len(plot_data)}
Correlation coefficient: {correlation:.3f}

X-axis statistics:
{plot_data[scatter_x].describe().to_string()}

Y-axis statistics:
{plot_data[scatter_y].describe().to_string()}"""
            )
    if len(context_parts) == 1:
        return "No chart information is currently avaliable"

    return "\n\n".join(context_parts)   


def build_analysis_prompt(dataset_context: str, user_question: str) -> str:
    """Combine dataset context and a user question into an AI analysis prompt."""
    if not isinstance(dataset_context, str) or not dataset_context.strip():
        raise ValueError("dataset_context must be a non-empty string.")

    if not isinstance(user_question, str) or not user_question.strip():
        raise ValueError("user_question must be a non-empty string.")

    return f"""INSTRUCTIONS
You are a helpful data analyst assistant. Answer using only the provided
dataset context. Do not invent values or facts that are not present in the
context. Clearly say when the available information is insufficient to answer
the question. Explain findings in beginner-friendly language and keep your
answer concise but useful.

DATASET CONTEXT
{dataset_context}

USER QUESTION
{user_question}
"""


def build_local_analysis_prompt(df: pd.DataFrame, user_question: str) -> str:
    """Build a compact dataset-analysis prompt for the local Ollama model."""
    if not isinstance(user_question, str) or not user_question.strip():
        raise ValueError("user_question must be a non-empty string.")

    rows, columns = get_dataset_shape(df)
    duplicate_count = get_duplicate_count(df)
    missing_values = get_missing_values(df)
    outlier_summary = get_outlier_summary(df)

    # Keep only columns that actually contain missing values.
    missing_values = missing_values[missing_values > 0]

    dataset_information = "\n\n".join(
        [
            f"Dataset Overview\nRows: {rows}\nColumns: {columns}",
            f"Duplicate Rows: {duplicate_count}",
            (
                "Missing Values\n"
                + (
                    missing_values.to_string()
                    if not missing_values.empty
                    else "No missing values."
                )
            ),
            (
                "Potential Outliers\n"
                + (
                    outlier_summary.to_string(index=False)
                    if not outlier_summary.empty
                    else "No potential outliers detected."
                )
            ),
        ]
    )

    return f"""INSTRUCTIONS
You are a helpful data analyst assistant.

Answer the question using only this dataset analysis.
Be concise. Do not explain your reasoning.
Do not invent values or facts.
Do not describe your reasoning process.
Do not speculate about the dataset or its purpose.
If the information is insufficient, clearly say so.
Keep the answer concise: 2-4 sentences or up to 3 bullet points.

DATASET ANALYSIS
{dataset_information}

USER QUESTION: {user_question}
"""

def build_computed_answer_context(df, user_question: str) -> str:
    """Calculate common dataset questions using Pandas and return verified results."""
    import re
    import pandas as pd

    question = user_question.lower()
    columns = {str(col).lower(): col for col in df.columns}

    # Common ways users refer to dataset columns.
    aliases = {
        "height": ["tallest", "taller", "tall", "shortest", "shorter", "short"],
        "weight": ["heaviest", "heavier", "heavy", "lightest", "lighter", "light"],
        "age": ["oldest", "old", "youngest", "young"],
        "price": ["most expensive", "expensive", "cheapest", "cheap"],
        "salary": ["highest paid", "lowest paid", "highest salary"],
    }

    # Identify a column mentioned directly in the question.
    def find_column(text):
        for col_lower, original_col in columns.items():
            if re.search(
                r"\b" + re.escape(col_lower) + r"\b",
                text,
            ):
                return original_col

        # Identify common semantic aliases.
        for col_lower, words in aliases.items():
            if col_lower in columns:
                for word in words:
                    if word in text:
                        return columns[col_lower]

        return None

    results = []

    # Identify common operations requested by the user.
    operations = []

    if re.search(r"\b(average|mean|avg)\b", question):
        operations.append("mean")

    if re.search(
        r"\b(maximum|max|highest|tallest|heaviest|largest|biggest)\b",
        question,
    ):
        operations.append("max")

    if re.search(
        r"\b(minimum|min|lowest|shortest|lightest|smallest)\b",
        question,
    ):
        operations.append("min")

    if re.search(r"\b(sum|total)\b", question):
        operations.append("sum")

    if re.search(r"\b(count|how many|number of)\b", question):
        operations.append("count")

    # Remove duplicate operations while preserving order.
    operations = list(dict.fromkeys(operations))

    if not operations:
        return ""

    # Find the entity/name column for identifying matching rows.
    entity_column = next(
        (
            col for col in df.columns
            if str(col).lower() in ["name", "pokemon", "title", "label"]
        ),
        None,
    )

    for operation in operations:
        column = find_column(question)

        if operation == "count":
            results.append(
                f"Row count: {len(df)}"
            )
            continue

        if column is None:
            continue

        numeric_values = pd.to_numeric(df[column], errors="coerce")
        valid = numeric_values.dropna()

        if valid.empty:
            continue

        if operation == "mean":
            value = valid.mean()
            results.append(
                f"Average of {column}: {value:.4f}"
            )

        elif operation == "sum":
            value = valid.sum()
            results.append(
                f"Sum of {column}: {value:.4f}"
            )

        elif operation == "max":
            value = valid.max()
            matching_rows = df.loc[numeric_values == value]

            if entity_column is not None:
                names = matching_rows[entity_column].astype(str).tolist()
                results.append(
                    f"Maximum {column}: {value}. "
                    f"Matching {entity_column}: {', '.join(names)}"
                )
            else:
                results.append(
                    f"Maximum {column}: {value}. "
                    f"Matching rows:\n{matching_rows.to_string(index=False)}"
                )

        elif operation == "min":
            value = valid.min()
            matching_rows = df.loc[numeric_values == value]

            if entity_column is not None:
                names = matching_rows[entity_column].astype(str).tolist()
                results.append(
                    f"Minimum {column}: {value}. "
                    f"Matching {entity_column}: {', '.join(names)}"
                )
            else:
                results.append(
                    f"Minimum {column}: {value}. "
                    f"Matching rows:\n{matching_rows.to_string(index=False)}"
                )

    if not results:
        return ""

    return (
        "VERIFIED RESULTS CALCULATED DIRECTLY FROM THE DATASET:\n"
        + "\n".join(results)
        + "\nUse these results as the source of truth. "
          "Do not invent values or entity names."
    )