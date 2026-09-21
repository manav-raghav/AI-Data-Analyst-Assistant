"""Simple functions for exploring a dataset."""

import pandas as pd


def get_dataset_shape(df: pd.DataFrame) -> tuple[int, int]:      #tuple[int, int]: this is a type hint it tells us the functions returns us a tuple of two integers, the number of rows and columns in the dataset
    """Return the number of rows and columns in the dataset."""
    return df.shape


def get_data_types(df: pd.DataFrame) -> pd.Series:
    """Return the data type for every column."""
    return df.dtypes


def get_missing_values(df: pd.DataFrame) -> pd.Series:
    """Return the number of missing values in every column."""
    return df.isnull().sum()


def get_duplicate_count(df: pd.DataFrame) -> int:
    """Return the total number of duplicate rows."""
    return int(df.duplicated().sum())


def get_numeric_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Return descriptive statistics for numeric columns."""
    return df.describe(include="number")


def get_correlation_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Return correlations between numeric columns."""
    return df.corr(numeric_only=True)


def get_outlier_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Return potential IQR-based outliers found in each numeric column.

    Missing values are ignored when calculating the bounds and counting outliers.
    """
    outlier_rows = []
    numerical_data = df.select_dtypes(include="number")

    for column in numerical_data.columns:
        values = numerical_data[column].dropna()
        q1 = values.quantile(0.25)
        q3 = values.quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        outlier_count = ((values < lower_bound) | (values > upper_bound)).sum()

        if outlier_count > 0:
            outlier_rows.append(
                {
                    "Column": column,
                    "Outlier Count": int(outlier_count),
                    "Lower Bound": lower_bound,
                    "Upper Bound": upper_bound,
                }
            )

    return pd.DataFrame(
        outlier_rows,
        columns=["Column", "Outlier Count", "Lower Bound", "Upper Bound"],
    )
