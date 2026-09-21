import matplotlib.pyplot as plt
import pandas as pd


def create_histogram(df: pd.DataFrame, column: str):
    """Create and return a histogram for a numeric DataFrame column."""
    figure, axis = plt.subplots()

    if column not in df.columns or not pd.api.types.is_numeric_dtype(df[column]):
        axis.text(
            0.5,
            0.5,
            "Please select a valid numeric column.",
            ha="center",
            va="center",
        )
        axis.set_axis_off()
        return figure

    axis.hist(df[column].dropna(), bins=10, edgecolor="black")
    axis.set_title(f"Distribution of {column}")
    axis.set_xlabel(column)
    axis.set_ylabel("Frequency")

    return figure
