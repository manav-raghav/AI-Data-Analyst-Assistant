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



def create_bar_chart(df: pd.DataFrame, column: str):
    """Create and return a bar chart for a DataFrame column."""
    figure, axis = plt.subplots()

    if column not in df.columns:
        axis.text(
            0.5,
            0.5,
            "Please select a valid column.",
            ha="center",
            va="center",
        )
        axis.set_axis_off()
        return figure

    counts = (
        df[column]
        .dropna()
        .astype(str)
        .str.strip()
        .str.title()
        .value_counts()
        
    )
    # Keep the top 10 categories
    top_counts = counts.head(10)

    # Combine the remaining categories into "Other"
    if len(counts) > 10:
        other_count = counts.iloc[10:].sum()
        top_counts.loc["Other"] = other_count

    counts = top_counts
    if counts.empty:
        axis.text(
            0.5,
            0.5,
            "No data available for this column.",
            ha="center",
            va="center",
        )
        axis.set_axis_off()
        return figure

    axis.barh(counts.index[::-1], counts.values[::-1], edgecolor="black")
    axis.set_xscale("log")
    axis.set_title(f"Frequency of {column}")
    axis.set_xlabel("Count (log scale)")
    axis.set_ylabel(column)
    axis.tick_params(axis="x", rotation=45)

    figure.tight_layout()

    return figure
    
def create_scatter_plot(
    df: pd.DataFrame,
    x_column: str,
    y_column: str,
):
    """Create and return a scatter plot for two numeric DataFrame columns."""
    figure, axis = plt.subplots()

    # Validate the selected columns
    if (
        x_column not in df.columns
        or y_column not in df.columns
        or not pd.api.types.is_numeric_dtype(df[x_column])
        or not pd.api.types.is_numeric_dtype(df[y_column])
    ):
        axis.text(
            0.5,
            0.5,
            "Please select valid numeric columns.",
            ha="center",
            va="center",
        )
        axis.set_axis_off()
        return figure

    # Remove rows with missing values in either column
    plot_data = df[[x_column, y_column]].dropna()

    if plot_data.empty:
        axis.text(
            0.5,
            0.5,
            "No data available for the selected columns.",
            ha="center",
            va="center",
        )
        axis.set_axis_off()
        return figure

    # Create the scatter plot
    axis.scatter(
        plot_data[x_column],
        plot_data[y_column],
        alpha=0.6,
        edgecolors="black",
    )

    axis.set_title(f"{y_column} vs. {x_column}")
    axis.set_xlabel(x_column)
    axis.set_ylabel(y_column)

    figure.tight_layout()

    return figure