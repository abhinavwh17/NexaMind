import math

import pandas as pd


# =========================================================
# Supported read-only operations
# =========================================================

SUPPORTED_OPERATIONS = {
    "SUM",
    "AVERAGE",
    "MIN",
    "MAX",
    "COUNT",
    "COUNT_DISTINCT",
    "MEDIAN",
    "STDDEV",
    "VARIANCE",
    "GROUP_BY",
    "GROUP_BY_METRICS",
    "DISTINCT_VALUES",
    "FIRST",
    "LAST",
}


# =========================================================
# Operations that must never modify source data
# =========================================================

FORBIDDEN_OPERATIONS = {
    "DELETE",
    "DROP",
    "UPDATE",
    "INSERT",
    "OVERWRITE",
    "RENAME",
    "REPLACE",
    "CLEAR",
    "REMOVE",
    "APPEND",
    "WRITE",
    "SAVE",
    "TRUNCATE",
}


# =========================================================
# Aggregations
# =========================================================

AGGREGATION_FUNCTIONS = {
    "SUM": "sum",
    "AVERAGE": "mean",
    "MIN": "min",
    "MAX": "max",
    "COUNT": "count",
    "COUNT_DISTINCT": "nunique",
    "MEDIAN": "median",
    "STDDEV": "std",
    "VARIANCE": "var",
}


SUPPORTED_GROUP_AGGREGATIONS = set(
    AGGREGATION_FUNCTIONS.keys()
)


# =========================================================
# Filters
# =========================================================

SUPPORTED_FILTER_OPERATORS = {
    "=",
    "!=",
    ">",
    ">=",
    "<",
    "<=",
    "IN",
    "NOT_IN",
    "CONTAINS",
    "NOT_CONTAINS",
    "BETWEEN",
    "IS_NULL",
    "IS_NOT_NULL",
    "LAST_MONTH",
    "THIS_MONTH",
}


# =========================================================
# Derived calculations
# =========================================================

SUPPORTED_DERIVED_OPERATIONS = {
    "ADD",
    "SUBTRACT",
    "MULTIPLY",
    "DIVIDE",
    "PERCENTAGE",
}


# =========================================================
# General helpers
# =========================================================


def normalize_value(value):

    if value is None:
        return None

    try:
        if pd.isna(value):
            return None

    except (
        TypeError,
        ValueError
    ):
        pass

    if hasattr(
        value,
        "item"
    ):
        value = value.item()

    if isinstance(
        value,
        float
    ):

        if math.isnan(value):
            return None

        if math.isinf(value):
            return None

    return value


def get_numeric_series(
    dataframe: pd.DataFrame,
    column: str
):

    return pd.to_numeric(
        dataframe[column],
        errors="coerce"
    )


def is_numeric_aggregation(
    aggregation: str
):

    return aggregation in {
        "SUM",
        "AVERAGE",
        "MIN",
        "MAX",
        "MEDIAN",
        "STDDEV",
        "VARIANCE",
    }


# =========================================================
# Group-by helper
# =========================================================


def normalize_group_by(
    group_by
):
    """
    Accept:

    "Party"

    OR

    ["Party", "VARIETY"]

    Always return a list internally.
    """

    if isinstance(
        group_by,
        str
    ):

        if not group_by.strip():

            raise ValueError(
                "group_by cannot be empty"
            )

        return [
            group_by
        ]

    if isinstance(
        group_by,
        list
    ):

        if not group_by:

            raise ValueError(
                "group_by cannot be empty"
            )

        for column in group_by:

            if (
                not isinstance(
                    column,
                    str
                )
                or
                not column.strip()
            ):

                raise ValueError(
                    "Every group_by value must be a column name"
                )

        return group_by

    raise ValueError(
        "group_by must be a string or array of strings"
    )


# =========================================================
# Generic aggregation
# =========================================================


def calculate_aggregation(
    dataframe: pd.DataFrame,
    column: str,
    aggregation: str
):

    aggregation = (
        aggregation.upper()
    )

    if (
        aggregation
        not in AGGREGATION_FUNCTIONS
    ):

        raise ValueError(
            f"Unsupported aggregation: {aggregation}"
        )

    if aggregation == "COUNT":

        return dataframe[
            column
        ].count()

    if aggregation == "COUNT_DISTINCT":

        return dataframe[
            column
        ].nunique(
            dropna=True
        )

    series = get_numeric_series(
        dataframe,
        column
    )

    if aggregation == "SUM":

        return series.sum()

    if aggregation == "AVERAGE":

        return series.mean()

    if aggregation == "MIN":

        return series.min()

    if aggregation == "MAX":

        return series.max()

    if aggregation == "MEDIAN":

        return series.median()

    if aggregation == "STDDEV":

        return series.std()

    if aggregation == "VARIANCE":

        return series.var()

    raise ValueError(
        f"Aggregation not implemented: {aggregation}"
    )


# =========================================================
# String helper
# =========================================================


def normalize_string_series(
    series: pd.Series
):

    return (
        series
        .astype(str)
        .str.strip()
        .str.casefold()
    )


# =========================================================
# Comparison helper
# =========================================================


def prepare_comparison_series(
    series: pd.Series,
    value
):

    # Existing datetime column

    if (
        pd.api.types
        .is_datetime64_any_dtype(
            series
        )
    ):

        parsed_value = pd.to_datetime(
            value,
            errors="coerce"
        )

        if pd.isna(
            parsed_value
        ):

            raise ValueError(
                f"Invalid date value: {value}"
            )

        return (
            pd.to_datetime(
                series,
                errors="coerce"
            ),
            parsed_value
        )

    # Existing numeric column

    if (
        pd.api.types
        .is_numeric_dtype(
            series
        )
    ):

        try:

            comparison_value = (
                float(
                    value
                )
            )

        except (
            TypeError,
            ValueError
        ) as error:

            raise ValueError(
                f"Invalid numeric value: {value}"
            ) from error

        return (
            pd.to_numeric(
                series,
                errors="coerce"
            ),
            comparison_value
        )

    # Try date conversion for string/object column

    parsed_value = pd.to_datetime(
        value,
        errors="coerce"
    )

    if not pd.isna(
        parsed_value
    ):

        parsed_series = (
            pd.to_datetime(
                series,
                errors="coerce"
            )
        )

        valid_ratio = (
            parsed_series
            .notna()
            .mean()
        )

        if valid_ratio >= 0.5:

            return (
                parsed_series,
                parsed_value
            )

    # Try numeric conversion

    try:

        numeric_value = (
            float(
                value
            )
        )

        numeric_series = (
            pd.to_numeric(
                series,
                errors="coerce"
            )
        )

        valid_ratio = (
            numeric_series
            .notna()
            .mean()
        )

        if valid_ratio >= 0.5:

            return (
                numeric_series,
                numeric_value
            )

    except (
        TypeError,
        ValueError
    ):
        pass

    # String fallback

    return (
        normalize_string_series(
            series
        ),
        str(value)
        .strip()
        .casefold()
    )


# =========================================================
# Apply filters
# =========================================================


def apply_filters(
    dataframe: pd.DataFrame,
    filters: list[dict] | None
):

    # Always work on a copy.
    # Never mutate uploaded source data.

    filtered_dataframe = (
        dataframe.copy()
    )

    if not filters:

        return filtered_dataframe

    for filter_item in filters:

        column = (
            filter_item.get(
                "column"
            )
        )

        operator = str(
            filter_item.get(
                "operator",
                ""
            )
        ).upper()

        value = (
            filter_item.get(
                "value"
            )
        )

        if (
            column
            not in filtered_dataframe.columns
        ):

            raise ValueError(
                f"Invalid filter column: {column}"
            )

        if (
            operator
            not in SUPPORTED_FILTER_OPERATORS
        ):

            raise ValueError(
                f"Unsupported filter operator: {operator}"
            )

        series = (
            filtered_dataframe[
                column
            ]
        )

        # -------------------------------------------------
        # IS NULL
        # -------------------------------------------------

        if operator == "IS_NULL":

            filtered_dataframe = (
                filtered_dataframe[
                    series.isna()
                ]
            )

            continue

        # -------------------------------------------------
        # IS NOT NULL
        # -------------------------------------------------

        if operator == "IS_NOT_NULL":

            filtered_dataframe = (
                filtered_dataframe[
                    series.notna()
                ]
            )

            continue

        # -------------------------------------------------
        # =
        # -------------------------------------------------

        if operator == "=":

            normalized_series = (
                normalize_string_series(
                    series
                )
            )

            normalized_value = (
                str(value)
                .strip()
                .casefold()
            )

            filtered_dataframe = (
                filtered_dataframe[
                    normalized_series
                    ==
                    normalized_value
                ]
            )

            continue

        # -------------------------------------------------
        # !=
        # -------------------------------------------------

        if operator == "!=":

            normalized_series = (
                normalize_string_series(
                    series
                )
            )

            normalized_value = (
                str(value)
                .strip()
                .casefold()
            )

            filtered_dataframe = (
                filtered_dataframe[
                    normalized_series
                    !=
                    normalized_value
                ]
            )

            continue

        # -------------------------------------------------
        # CONTAINS
        # -------------------------------------------------

        if operator == "CONTAINS":

            normalized_series = (
                normalize_string_series(
                    series
                )
            )

            normalized_value = (
                str(value)
                .strip()
                .casefold()
            )

            mask = (
                normalized_series
                .str.contains(
                    normalized_value,
                    na=False,
                    regex=False
                )
            )

            filtered_dataframe = (
                filtered_dataframe[
                    mask
                ]
            )

            continue

        # -------------------------------------------------
        # NOT_CONTAINS
        # -------------------------------------------------

        if operator == "NOT_CONTAINS":

            normalized_series = (
                normalize_string_series(
                    series
                )
            )

            normalized_value = (
                str(value)
                .strip()
                .casefold()
            )

            mask = ~(
                normalized_series
                .str.contains(
                    normalized_value,
                    na=False,
                    regex=False
                )
            )

            filtered_dataframe = (
                filtered_dataframe[
                    mask
                ]
            )

            continue

        # -------------------------------------------------
        # IN / NOT_IN
        # -------------------------------------------------

        if operator in {
            "IN",
            "NOT_IN",
        }:

            if not isinstance(
                value,
                list
            ):

                raise ValueError(
                    f"{operator} requires an array"
                )

            normalized_values = [
                str(item)
                .strip()
                .casefold()

                for item in value
            ]

            normalized_series = (
                normalize_string_series(
                    series
                )
            )

            mask = (
                normalized_series
                .isin(
                    normalized_values
                )
            )

            if operator == "NOT_IN":

                mask = ~mask

            filtered_dataframe = (
                filtered_dataframe[
                    mask
                ]
            )

            continue

        # -------------------------------------------------
        # BETWEEN
        # -------------------------------------------------

        if operator == "BETWEEN":

            if (
                not isinstance(
                    value,
                    list
                )
                or
                len(value) != 2
            ):

                raise ValueError(
                    "BETWEEN requires [from, to]"
                )

            (
                comparison_series,
                start
            ) = prepare_comparison_series(
                series,
                value[0]
            )

            (
                _,
                end
            ) = prepare_comparison_series(
                series,
                value[1]
            )

            mask = (
                comparison_series
                >=
                start
            ) & (
                comparison_series
                <=
                end
            )

            filtered_dataframe = (
                filtered_dataframe[
                    mask
                ]
            )

            continue

        # -------------------------------------------------
        # Comparison operators
        # -------------------------------------------------

        if operator in {
            ">",
            ">=",
            "<",
            "<=",
        }:

            (
                comparison_series,
                comparison_value
            ) = prepare_comparison_series(
                series,
                value
            )

            if operator == ">":

                mask = (
                    comparison_series
                    >
                    comparison_value
                )

            elif operator == ">=":

                mask = (
                    comparison_series
                    >=
                    comparison_value
                )

            elif operator == "<":

                mask = (
                    comparison_series
                    <
                    comparison_value
                )

            else:

                mask = (
                    comparison_series
                    <=
                    comparison_value
                )

            filtered_dataframe = (
                filtered_dataframe[
                    mask
                ]
            )

            continue

        # -------------------------------------------------
        # LAST_MONTH
        # -------------------------------------------------

        if operator == "LAST_MONTH":

            dates = pd.to_datetime(
                series,
                errors="coerce"
            )

            today = (
                pd.Timestamp.now()
            )

            first_day_this_month = (
                pd.Timestamp(
                    year=today.year,
                    month=today.month,
                    day=1
                )
            )

            first_day_last_month = (
                first_day_this_month
                -
                pd.offsets.MonthBegin(1)
            )

            mask = (
                dates
                >=
                first_day_last_month
            ) & (
                dates
                <
                first_day_this_month
            )

            filtered_dataframe = (
                filtered_dataframe[
                    mask
                ]
            )

            continue

        # -------------------------------------------------
        # THIS_MONTH
        # -------------------------------------------------

        if operator == "THIS_MONTH":

            dates = pd.to_datetime(
                series,
                errors="coerce"
            )

            today = (
                pd.Timestamp.now()
            )

            first_day_this_month = (
                pd.Timestamp(
                    year=today.year,
                    month=today.month,
                    day=1
                )
            )

            first_day_next_month = (
                first_day_this_month
                +
                pd.offsets.MonthBegin(1)
            )

            mask = (
                dates
                >=
                first_day_this_month
            ) & (
                dates
                <
                first_day_next_month
            )

            filtered_dataframe = (
                filtered_dataframe[
                    mask
                ]
            )

            continue

    return filtered_dataframe


# =========================================================
# Filter validation
# =========================================================


def validate_filters(
    filters,
    columns
):

    if not isinstance(
        filters,
        list
    ):

        raise ValueError(
            "filters must be an array"
        )

    for filter_item in filters:

        if not isinstance(
            filter_item,
            dict
        ):

            raise ValueError(
                "Each filter must be an object"
            )

        column = (
            filter_item.get(
                "column"
            )
        )

        operator = str(
            filter_item.get(
                "operator",
                ""
            )
        ).upper()

        if column not in columns:

            raise ValueError(
                f"Invalid filter column: {column}"
            )

        if (
            operator
            not in SUPPORTED_FILTER_OPERATORS
        ):

            raise ValueError(
                f"Unsupported filter operator: {operator}"
            )


# =========================================================
# Validate group-by columns
# =========================================================


def validate_group_by(
    group_by,
    columns
):

    group_by_columns = (
        normalize_group_by(
            group_by
        )
    )

    for group_column in group_by_columns:

        if group_column not in columns:

            raise ValueError(
                "Invalid group_by column: "
                f"{group_column}"
            )

    return group_by_columns


# =========================================================
# Calculation validation
# =========================================================


def validate_calculation(
    calculation: dict,
    sheets: dict
):

    calculation_id = (
        calculation.get(
            "id"
        )
    )

    operation = str(
        calculation.get(
            "operation",
            ""
        )
    ).upper()

    sheet_name = (
        calculation.get(
            "sheet"
        )
    )

    if not calculation_id:

        raise ValueError(
            "Calculation requires id"
        )

    # -----------------------------------------------------
    # Mutation protection
    # -----------------------------------------------------

    if (
        operation
        in FORBIDDEN_OPERATIONS
    ):

        raise ValueError(
            "Data modification is not allowed: "
            f"{operation}"
        )

    if (
        operation
        not in SUPPORTED_OPERATIONS
    ):

        raise ValueError(
            f"Unsupported operation: {operation}"
        )

    if sheet_name not in sheets:

        raise ValueError(
            f"Invalid sheet: {sheet_name}"
        )

    dataframe = (
        sheets[
            sheet_name
        ]
    )

    columns = [
        str(column)
        for column
        in dataframe.columns
    ]

    filters = (
        calculation.get(
            "filters",
            []
        )
    )

    validate_filters(
        filters,
        columns
    )

    # =====================================================
    # GROUP_BY_METRICS
    # =====================================================

    if operation == "GROUP_BY_METRICS":

        group_by = (
            calculation.get(
                "group_by"
            )
        )

        validate_group_by(
            group_by,
            columns
        )

        metrics = (
            calculation.get(
                "metrics"
            )
        )

        if (
            not isinstance(
                metrics,
                list
            )
            or
            not metrics
        ):

            raise ValueError(
                "GROUP_BY_METRICS requires metrics[]"
            )

        aliases = set()

        for metric in metrics:

            if not isinstance(
                metric,
                dict
            ):

                raise ValueError(
                    "Each metric must be an object"
                )

            metric_column = (
                metric.get(
                    "column"
                )
            )

            aggregation = str(
                metric.get(
                    "aggregation",
                    ""
                )
            ).upper()

            alias = (
                metric.get(
                    "alias"
                )
            )

            if metric_column not in columns:

                raise ValueError(
                    "Invalid metric column: "
                    f"{metric_column}"
                )

            if (
                aggregation
                not in SUPPORTED_GROUP_AGGREGATIONS
            ):

                raise ValueError(
                    "Unsupported aggregation: "
                    f"{aggregation}"
                )

            if not alias:

                raise ValueError(
                    "Metric requires alias"
                )

            if alias in aliases:

                raise ValueError(
                    f"Duplicate metric alias: {alias}"
                )

            aliases.add(
                alias
            )

        # -------------------------------------------------
        # Derived calculations
        # -------------------------------------------------

        derived_items = (
            calculation.get(
                "derived",
                []
            )
        )

        if not isinstance(
            derived_items,
            list
        ):

            raise ValueError(
                "derived must be an array"
            )

        available_names = set(
            aliases
        )

        for derived in derived_items:

            if not isinstance(
                derived,
                dict
            ):

                raise ValueError(
                    "Each derived calculation must be an object"
                )

            name = (
                derived.get(
                    "name"
                )
            )

            derived_operation = str(
                derived.get(
                    "operation",
                    ""
                )
            ).upper()

            left = (
                derived.get(
                    "left"
                )
            )

            right = (
                derived.get(
                    "right"
                )
            )

            if not name:

                raise ValueError(
                    "Derived calculation requires name"
                )

            if (
                derived_operation
                not in SUPPORTED_DERIVED_OPERATIONS
            ):

                raise ValueError(
                    "Unsupported derived operation: "
                    f"{derived_operation}"
                )

            if left not in available_names:

                raise ValueError(
                    f"Unknown operand: {left}"
                )

            if right not in available_names:

                raise ValueError(
                    f"Unknown operand: {right}"
                )

            available_names.add(
                name
            )

        return

    # =====================================================
    # Normal calculations
    # =====================================================

    column = (
        calculation.get(
            "column"
        )
    )

    if column not in columns:

        raise ValueError(
            f"Invalid column: {column}"
        )

    # =====================================================
    # GROUP_BY
    # =====================================================

    if operation == "GROUP_BY":

        group_by = (
            calculation.get(
                "group_by"
            )
        )

        validate_group_by(
            group_by,
            columns
        )

        aggregation = str(
            calculation.get(
                "aggregation",
                "SUM"
            )
        ).upper()

        if (
            aggregation
            not in SUPPORTED_GROUP_AGGREGATIONS
        ):

            raise ValueError(
                "Unsupported aggregation: "
                f"{aggregation}"
            )


# =========================================================
# Generic grouped calculation
# =========================================================


def calculate_grouped(
    dataframe: pd.DataFrame,
    group_by,
    column: str,
    aggregation: str,
    sort="DESC",
    limit=None
):

    aggregation = (
        aggregation.upper()
    )

    if (
        aggregation
        not in SUPPORTED_GROUP_AGGREGATIONS
    ):

        raise ValueError(
            f"Unsupported aggregation: {aggregation}"
        )

    # -----------------------------------------------------
    # SINGLE or MULTIPLE group-by columns
    # -----------------------------------------------------

    group_by_columns = (
        normalize_group_by(
            group_by
        )
    )

    working_columns = (
        group_by_columns
        +
        [
            column
        ]
    )

    # Avoid duplicate column selection
    working_columns = list(
        dict.fromkeys(
            working_columns
        )
    )

    working_dataframe = (
        dataframe[
            working_columns
        ]
        .copy()
    )

    # -----------------------------------------------------
    # Numeric conversion
    # -----------------------------------------------------

    if is_numeric_aggregation(
        aggregation
    ):

        working_dataframe[
            column
        ] = (
            pd.to_numeric(
                working_dataframe[
                    column
                ],
                errors="coerce"
            )
        )

    # -----------------------------------------------------
    # Remove rows missing grouping fields
    # -----------------------------------------------------

    required_columns = list(
        group_by_columns
    )

    if column not in required_columns:

        required_columns.append(
            column
        )

    working_dataframe = (
        working_dataframe
        .dropna(
            subset=required_columns
        )
    )

    # -----------------------------------------------------
    # Group
    # -----------------------------------------------------

    grouped = (
        working_dataframe
        .groupby(
            group_by_columns,
            as_index=False,
            dropna=False
        )
    )

    # -----------------------------------------------------
    # Aggregation
    # -----------------------------------------------------

    if aggregation == "COUNT":

        result = (
            grouped[
                column
            ]
            .count()
        )

    elif aggregation == "COUNT_DISTINCT":

        result = (
            grouped[
                column
            ]
            .nunique()
        )

    else:

        pandas_function = (
            AGGREGATION_FUNCTIONS[
                aggregation
            ]
        )

        result = (
            grouped[
                column
            ]
            .agg(
                pandas_function
            )
        )

    # -----------------------------------------------------
    # Sort by aggregated metric
    # -----------------------------------------------------

    if sort:

        result = (
            result
            .sort_values(
                by=column,
                ascending=(
                    str(
                        sort
                    ).upper()
                    ==
                    "ASC"
                )
            )
        )

    # -----------------------------------------------------
    # Limit
    # -----------------------------------------------------

    if limit is not None:

        result = (
            result.head(
                int(
                    limit
                )
            )
        )

    return result


# =========================================================
# GROUP_BY_METRICS
# =========================================================


def execute_group_by_metrics(
    dataframe: pd.DataFrame,
    calculation: dict
):

    group_by = (
        calculation[
            "group_by"
        ]
    )

    group_by_columns = (
        normalize_group_by(
            group_by
        )
    )

    metrics = (
        calculation[
            "metrics"
        ]
    )

    result_dataframe = None

    # -----------------------------------------------------
    # Calculate every metric
    # -----------------------------------------------------

    for metric in metrics:

        column = (
            metric[
                "column"
            ]
        )

        aggregation = str(
            metric[
                "aggregation"
            ]
        ).upper()

        alias = (
            metric[
                "alias"
            ]
        )

        metric_dataframe = (
            calculate_grouped(
                dataframe=dataframe,
                group_by=group_by_columns,
                column=column,
                aggregation=aggregation,
                sort=None,
                limit=None
            )
        )

        metric_dataframe = (
            metric_dataframe.rename(
                columns={
                    column:
                        alias
                }
            )
        )

        # -------------------------------------------------
        # Merge metrics using ALL grouping columns
        # -------------------------------------------------

        if result_dataframe is None:

            result_dataframe = (
                metric_dataframe
            )

        else:

            result_dataframe = (
                result_dataframe.merge(
                    metric_dataframe,
                    on=group_by_columns,
                    how="outer"
                )
            )

    if result_dataframe is None:

        result_dataframe = (
            pd.DataFrame(
                columns=group_by_columns
            )
        )

    # -----------------------------------------------------
    # Derived calculations
    # -----------------------------------------------------

    derived_items = (
        calculation.get(
            "derived",
            []
        )
    )

    for derived in derived_items:

        name = (
            derived[
                "name"
            ]
        )

        operation = str(
            derived[
                "operation"
            ]
        ).upper()

        left = (
            derived[
                "left"
            ]
        )

        right = (
            derived[
                "right"
            ]
        )

        left_series = (
            pd.to_numeric(
                result_dataframe[
                    left
                ],
                errors="coerce"
            )
            .fillna(0)
        )

        right_series = (
            pd.to_numeric(
                result_dataframe[
                    right
                ],
                errors="coerce"
            )
            .fillna(0)
        )

        if operation == "ADD":

            result_dataframe[
                name
            ] = (
                left_series
                +
                right_series
            )

        elif operation == "SUBTRACT":

            result_dataframe[
                name
            ] = (
                left_series
                -
                right_series
            )

        elif operation == "MULTIPLY":

            result_dataframe[
                name
            ] = (
                left_series
                *
                right_series
            )

        elif operation == "DIVIDE":

            denominator = (
                right_series
                .replace(
                    0,
                    float("nan")
                )
            )

            result_dataframe[
                name
            ] = (
                left_series
                /
                denominator
            )

        elif operation == "PERCENTAGE":

            denominator = (
                right_series
                .replace(
                    0,
                    float("nan")
                )
            )

            result_dataframe[
                name
            ] = (
                (
                    left_series
                    /
                    denominator
                )
                *
                100
            )

        else:

            raise ValueError(
                "Unsupported derived operation: "
                f"{operation}"
            )

    # -----------------------------------------------------
    # Optional sorting
    # -----------------------------------------------------

    sort_by = (
        calculation.get(
            "sort_by"
        )
    )

    sort_direction = str(
        calculation.get(
            "sort",
            "DESC"
        )
    ).upper()

    if sort_by:

        if (
            sort_by
            not in result_dataframe.columns
        ):

            raise ValueError(
                f"Invalid sort_by column: {sort_by}"
            )

        result_dataframe = (
            result_dataframe
            .sort_values(
                by=sort_by,
                ascending=(
                    sort_direction
                    ==
                    "ASC"
                )
            )
        )

    # -----------------------------------------------------
    # Optional limit
    # -----------------------------------------------------

    limit = (
        calculation.get(
            "limit"
        )
    )

    if limit is not None:

        result_dataframe = (
            result_dataframe
            .head(
                int(
                    limit
                )
            )
        )

    return result_dataframe


# =========================================================
# Main executor
# =========================================================


def execute_calculation(
    sheets: dict,
    calculation: dict
):

    validate_calculation(
        calculation,
        sheets
    )

    calculation_id = (
        calculation[
            "id"
        ]
    )

    operation = str(
        calculation[
            "operation"
        ]
    ).upper()

    sheet_name = (
        calculation[
            "sheet"
        ]
    )

    # Always work on copy
    dataframe = (
        sheets[
            sheet_name
        ]
        .copy()
    )

    filters = (
        calculation.get(
            "filters",
            []
        )
    )

    dataframe = apply_filters(
        dataframe,
        filters
    )

    print(
        "\n========== FILTER RESULT =========="
    )

    print(
        "Filters:",
        filters
    )

    print(
        "Remaining rows:",
        len(
            dataframe
        )
    )

    print(
        "==================================="
    )

    result = {
        "id":
            calculation_id,

        "operation":
            operation,

        "sheet":
            sheet_name,
    }

    if filters:

        result[
            "filters"
        ] = filters

    # =====================================================
    # GROUP_BY_METRICS
    # =====================================================

    if operation == "GROUP_BY_METRICS":

        grouped_dataframe = (
            execute_group_by_metrics(
                dataframe,
                calculation
            )
        )

        rows = []

        records = (
            grouped_dataframe
            .to_dict(
                orient="records"
            )
        )

        for record in records:

            normalized_record = {
                key:
                    normalize_value(
                        value
                    )

                for key, value
                in record.items()
            }

            rows.append(
                normalized_record
            )

        result[
            "group_by"
        ] = calculation[
            "group_by"
        ]

        result[
            "metrics"
        ] = calculation[
            "metrics"
        ]

        result[
            "derived"
        ] = calculation.get(
            "derived",
            []
        )

        result[
            "rows"
        ] = rows

        return result

    # =====================================================
    # GROUP_BY
    # =====================================================

    if operation == "GROUP_BY":

        column = (
            calculation[
                "column"
            ]
        )

        group_by = (
            calculation[
                "group_by"
            ]
        )

        aggregation = str(
            calculation.get(
                "aggregation",
                "SUM"
            )
        ).upper()

        sort = (
            calculation.get(
                "sort",
                "DESC"
            )
        )

        limit = (
            calculation.get(
                "limit"
            )
        )

        grouped_dataframe = (
            calculate_grouped(
                dataframe=dataframe,
                group_by=group_by,
                column=column,
                aggregation=aggregation,
                sort=sort,
                limit=limit
            )
        )

        rows = []

        records = (
            grouped_dataframe
            .to_dict(
                orient="records"
            )
        )

        for record in records:

            rows.append({
                key:
                    normalize_value(
                        value
                    )

                for key, value
                in record.items()
            })

        result[
            "column"
        ] = column

        result[
            "group_by"
        ] = group_by

        result[
            "aggregation"
        ] = aggregation

        result[
            "rows"
        ] = rows

        # -------------------------------------------------
        # Single-result placeholder support
        # -------------------------------------------------

        if len(rows) == 1:

            group_by_columns = (
                normalize_group_by(
                    group_by
                )
            )

            if len(
                group_by_columns
            ) == 1:

                result[
                    "group"
                ] = (
                    rows[
                        0
                    ][
                        group_by_columns[
                            0
                        ]
                    ]
                )

            else:

                # Example:
                # WOOD - HUBLI / 6 ROW

                group_values = [
                    str(
                        rows[
                            0
                        ][
                            group_column
                        ]
                    )

                    for group_column
                    in group_by_columns
                ]

                result[
                    "group"
                ] = " / ".join(
                    group_values
                )

            result[
                "value"
            ] = (
                rows[
                    0
                ][
                    column
                ]
            )

        return result

    # =====================================================
    # DISTINCT_VALUES
    # =====================================================

    if operation == "DISTINCT_VALUES":

        column = (
            calculation[
                "column"
            ]
        )

        values = (
            dataframe[
                column
            ]
            .dropna()
            .drop_duplicates()
            .tolist()
        )

        result[
            "column"
        ] = column

        result[
            "values"
        ] = [
            normalize_value(
                value
            )
            for value
            in values
        ]

        result[
            "count"
        ] = len(
            values
        )

        return result

    # =====================================================
    # FIRST / LAST
    # =====================================================

    if operation in {
        "FIRST",
        "LAST",
    }:

        column = (
            calculation[
                "column"
            ]
        )

        values = (
            dataframe[
                column
            ]
            .dropna()
        )

        if values.empty:

            value = None

        elif operation == "FIRST":

            value = (
                values.iloc[
                    0
                ]
            )

        else:

            value = (
                values.iloc[
                    -1
                ]
            )

        result[
            "column"
        ] = column

        result[
            "value"
        ] = normalize_value(
            value
        )

        return result

    # =====================================================
    # Scalar aggregations
    # =====================================================

    if (
        operation
        in AGGREGATION_FUNCTIONS
    ):

        column = (
            calculation[
                "column"
            ]
        )

        value = (
            calculate_aggregation(
                dataframe=dataframe,
                column=column,
                aggregation=operation
            )
        )

        result[
            "column"
        ] = column

        result[
            "value"
        ] = normalize_value(
            value
        )

        return result

    raise ValueError(
        f"Operation not implemented: {operation}"
    )