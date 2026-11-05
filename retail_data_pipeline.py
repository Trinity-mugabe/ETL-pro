"""Prepare and export Walmart retail sales data."""

import os
from pathlib import Path

import pandas as pd


def extract(store_data: pd.DataFrame, extra_data: str | Path) -> pd.DataFrame:
    """Merge the PostgreSQL sales query result with complementary parquet data."""
    extra_df = pd.read_parquet(extra_data)
    return store_data.merge(extra_df, on="index")


def transform(raw_data: pd.DataFrame) -> pd.DataFrame:
    """Clean merged sales data and retain the analysis columns."""
    raw_data = raw_data.copy()
    raw_data.fillna(
        {
            "CPI": raw_data["CPI"].mean(),
            "Weekly_Sales": raw_data["Weekly_Sales"].mean(),
            "Unemployment": raw_data["Unemployment"].mean(),
        },
        inplace=True,
    )

    raw_data["Date"] = pd.to_datetime(raw_data["Date"], format="%Y-%m-%d")
    raw_data["Month"] = raw_data["Date"].dt.month
    raw_data = raw_data.loc[raw_data["Weekly_Sales"] > 10000, :]

    columns_to_drop = [
        "index",
        "Temperature",
        "Fuel_Price",
        "MarkDown1",
        "MarkDown2",
        "MarkDown3",
        "MarkDown4",
        "MarkDown5",
        "Type",
        "Size",
        "Date",
    ]
    raw_data = raw_data.drop(columns=columns_to_drop, errors="ignore")
    return raw_data[
        [
            "Store_ID",
            "Month",
            "Dept",
            "IsHoliday",
            "Weekly_Sales",
            "CPI",
            "Unemployment",
        ]
    ]


def avg_weekly_sales_per_month(clean_data: pd.DataFrame) -> pd.DataFrame:
    """Calculate average weekly sales for each month."""
    return (
        clean_data[["Month", "Weekly_Sales"]]
        .groupby("Month")
        .agg(Weekly_Sales=("Weekly_Sales", "mean"))
        .reset_index()
        .round(2)
    )


def load(
    full_data: pd.DataFrame,
    full_data_file_path: str | Path,
    agg_data: pd.DataFrame,
    agg_data_file_path: str | Path,
) -> None:
    """Save the cleaned and aggregated DataFrames as CSV files."""
    full_data.to_csv(full_data_file_path, index=False)
    agg_data.to_csv(agg_data_file_path, index=False)


def validation(file_path: str | Path) -> None:
    """Raise an error if an expected output file was not created."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"There is no file at the path {file_path}")


def run_pipeline(
    grocery_sales: pd.DataFrame,
    extra_data_path: str | Path = "extra_data.parquet",
    clean_data_path: str | Path = "clean_data.csv",
    agg_data_path: str | Path = "agg_data.csv",
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Run the pipeline using grocery sales loaded from PostgreSQL."""
    merged_df = extract(grocery_sales, extra_data_path)
    clean_data = transform(merged_df)
    agg_data = avg_weekly_sales_per_month(clean_data)

    load(clean_data, clean_data_path, agg_data, agg_data_path)
    validation(clean_data_path)
    validation(agg_data_path)

    return clean_data, agg_data
