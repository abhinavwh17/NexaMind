import pandas as pd


def calculate_sum(dataframe: pd.DataFrame, column: str):
    return dataframe[column].sum()


def calculate_average(dataframe: pd.DataFrame, column: str):
    return dataframe[column].mean()


def calculate_min(dataframe: pd.DataFrame, column: str):
    return dataframe[column].min()


def calculate_max(dataframe: pd.DataFrame, column: str):
    return dataframe[column].max()


def calculate_count(dataframe: pd.DataFrame, column: str):
    return dataframe[column].count()


def calculate_group_by_sum(
    dataframe: pd.DataFrame,
    group_by: str,
    column: str
):
    return (
        dataframe
        .groupby(group_by)[column]
        .sum()
        .sort_values(ascending=False)
    )