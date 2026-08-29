import math

import pandas as pd


SUPPORTED_OPERATIONS = {
    "SUM",
    "AVERAGE",
    "MIN",
    "MAX",
    "COUNT",
    "GROUP_BY",
    "GROUP_BY_METRICS",
}


SUPPORTED_FILTER_OPERATORS = {
    "=",
    "!=",
    ">",
    ">=",
    "<",
    "<=",
    "LAST_MONTH",
    "THIS_MONTH",
}


SUPPORTED_GROUP_AGGREGATIONS = {
    "SUM",
}


SUPPORTED_DERIVED_OPERATIONS = {
    "SUBTRACT",
}


# =========================================================
# Numeric helpers
# =========================================================


def numeric_series(
    dataframe: pd.DataFrame,
    column: str
):

    return pd.to_numeric(
        dataframe[column],
        errors="coerce"
    )


# =========================================================
# Basic calculations
# =========================================================


def calculate_sum(
    dataframe: pd.DataFrame,
    column: str
):

    return numeric_series(
        dataframe,
        column
    ).sum()


def calculate_average(
    dataframe: pd.DataFrame,
    column: str
):

    return numeric_series(
        dataframe,
        column
    ).mean()


def calculate_min(
    dataframe: pd.DataFrame,
    column: str
):

    return numeric_series(
        dataframe,
        column
    ).min()


def calculate_max(
    dataframe: pd.DataFrame,
    column: str
):

    return numeric_series(
        dataframe,
        column
    ).max()


def calculate_count(
    dataframe: pd.DataFrame,
    column: str
):

    return dataframe[column].count()


# =========================================================
# Grouped sum
# =========================================================


def calculate_grouped_sum(
    dataframe: pd.DataFrame,
    group_by: str,
    column: str,
    sort: str = "DESC",
    limit: int | None = None
):

    working_dataframe = dataframe[
        [
            group_by,
            column
        ]
    ].copy()

    working_dataframe[column] = (
        pd.to_numeric(
            working_dataframe[column],
            errors="coerce"
        )
    )

    working_dataframe = (
        working_dataframe
        .dropna(
            subset=[
                group_by,
                column
            ]
        )
    )

    result = (
        working_dataframe
        .groupby(
            group_by,
            as_index=False
        )[column]
        .sum()
    )

    ascending = (
        str(sort).upper()
        == "ASC"
    )

    result = result.sort_values(
        by=column,
        ascending=ascending
    )

    if limit is not None:

        result = result.head(
            int(limit)
        )

    return result


# =========================================================
# JSON normalization
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


# =========================================================
# Filters
# =========================================================


def prepare_comparison_value(
    series: pd.Series,
    value
):

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
                f"Invalid date filter value: {value}"
            )

        return parsed_value

    if (
        pd.api.types
        .is_numeric_dtype(
            series
        )
    ):

        try:

            return float(
                value
            )

        except (
            TypeError,
            ValueError
        ) as error:

            raise ValueError(
                f"Invalid numeric filter value: {value}"
            ) from error

    return value


def apply_filters(
    dataframe: pd.DataFrame,
    filters: list[dict] | None
):

    if not filters:
        return dataframe.copy()

    filtered_dataframe = (
        dataframe.copy()
    )

    for filter_item in filters:

        column = filter_item.get(
            "column"
        )

        operator = filter_item.get(
            "operator"
        )

        value = filter_item.get(
            "value"
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
        # =
        # -------------------------------------------------

        if operator == "=":

            if (
                pd.api.types
                .is_object_dtype(
                    series
                )
                or
                pd.api.types
                .is_string_dtype(
                    series
                )
            ):

                mask = (
                    series
                    .astype(str)
                    .str.strip()
                    .str.casefold()
                    ==
                    str(value)
                    .strip()
                    .casefold()
                )

            else:

                comparison_value = (
                    prepare_comparison_value(
                        series,
                        value
                    )
                )

                mask = (
                    series
                    ==
                    comparison_value
                )

            filtered_dataframe = (
                filtered_dataframe[
                    mask
                ]
            )

        # -------------------------------------------------
        # !=
        # -------------------------------------------------

        elif operator == "!=":

            if (
                pd.api.types
                .is_object_dtype(
                    series
                )
                or
                pd.api.types
                .is_string_dtype(
                    series
                )
            ):

                mask = (
                    series
                    .astype(str)
                    .str.strip()
                    .str.casefold()
                    !=
                    str(value)
                    .strip()
                    .casefold()
                )

            else:

                comparison_value = (
                    prepare_comparison_value(
                        series,
                        value
                    )
                )

                mask = (
                    series
                    !=
                    comparison_value
                )

            filtered_dataframe = (
                filtered_dataframe[
                    mask
                ]
            )

        # -------------------------------------------------
        # Numeric/date comparisons
        # -------------------------------------------------

        elif operator in {
            ">",
            ">=",
            "<",
            "<=",
        }:

            comparison_value = (
                prepare_comparison_value(
                    series,
                    value
                )
            )

            if operator == ">":

                mask = (
                    series
                    >
                    comparison_value
                )

            elif operator == ">=":

                mask = (
                    series
                    >=
                    comparison_value
                )

            elif operator == "<":

                mask = (
                    series
                    <
                    comparison_value
                )

            else:

                mask = (
                    series
                    <=
                    comparison_value
                )

            filtered_dataframe = (
                filtered_dataframe[
                    mask
                ]
            )

        # -------------------------------------------------
        # Last month
        # -------------------------------------------------

        elif operator == "LAST_MONTH":

            dates = pd.to_datetime(
                series,
                errors="coerce"
            )

            today = pd.Timestamp.now()

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
                (
                    dates
                    >=
                    first_day_last_month
                )
                &
                (
                    dates
                    <
                    first_day_this_month
                )
            )

            filtered_dataframe = (
                filtered_dataframe[
                    mask
                ]
            )

        # -------------------------------------------------
        # This month
        # -------------------------------------------------

        elif operator == "THIS_MONTH":

            dates = pd.to_datetime(
                series,
                errors="coerce"
            )

            today = pd.Timestamp.now()

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
                (
                    dates
                    >=
                    first_day_this_month
                )
                &
                (
                    dates
                    <
                    first_day_next_month
                )
            )

            filtered_dataframe = (
                filtered_dataframe[
                    mask
                ]
            )

    return filtered_dataframe


# =========================================================
# Validation
# =========================================================


def validate_filters(
    filters: list[dict],
    columns: list[str]
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

        filter_column = (
            filter_item.get(
                "column"
            )
        )

        filter_operator = (
            filter_item.get(
                "operator"
            )
        )

        if filter_column not in columns:

            raise ValueError(
                f"Invalid filter column: {filter_column}"
            )

        if (
            filter_operator
            not in SUPPORTED_FILTER_OPERATORS
        ):

            raise ValueError(
                f"Unsupported filter operator: {filter_operator}"
            )


def validate_calculation(
    calculation: dict,
    sheets: dict
):

    calculation_id = (
        calculation.get(
            "id"
        )
    )

    operation = (
        calculation.get(
            "operation"
        )
    )

    sheet_name = (
        calculation.get(
            "sheet"
        )
    )

    if not calculation_id:

        raise ValueError(
            "Calculation is missing id"
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

    dataframe = sheets[
        sheet_name
    ]

    columns = [
        str(column_name)
        for column_name
        in dataframe.columns
    ]

    filters = calculation.get(
        "filters",
        []
    )

    validate_filters(
        filters,
        columns
    )

    # =====================================================
    # GROUP_BY_METRICS
    # =====================================================

    if operation == "GROUP_BY_METRICS":

        group_by = calculation.get(
            "group_by"
        )

        if not group_by:

            raise ValueError(
                "GROUP_BY_METRICS requires group_by"
            )

        if group_by not in columns:

            raise ValueError(
                f"Invalid group_by column: {group_by}"
            )

        metrics = calculation.get(
            "metrics"
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

        metric_aliases = set()

        for metric in metrics:

            metric_column = (
                metric.get(
                    "column"
                )
            )

            aggregation = (
                metric.get(
                    "aggregation"
                )
            )

            alias = metric.get(
                "alias"
            )

            if metric_column not in columns:

                raise ValueError(
                    f"Invalid metric column: {metric_column}"
                )

            if (
                aggregation
                not in SUPPORTED_GROUP_AGGREGATIONS
            ):

                raise ValueError(
                    f"Unsupported aggregation: {aggregation}"
                )

            if not alias:

                raise ValueError(
                    "Every metric requires alias"
                )

            if alias in metric_aliases:

                raise ValueError(
                    f"Duplicate metric alias: {alias}"
                )

            metric_aliases.add(
                alias
            )

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
            metric_aliases
        )

        for derived in derived_items:

            name = derived.get(
                "name"
            )

            derived_operation = (
                derived.get(
                    "operation"
                )
            )

            left = derived.get(
                "left"
            )

            right = derived.get(
                "right"
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
                    f"Unsupported derived operation: {derived_operation}"
                )

            if left not in available_names:

                raise ValueError(
                    f"Unknown left operand: {left}"
                )

            if right not in available_names:

                raise ValueError(
                    f"Unknown right operand: {right}"
                )

            available_names.add(
                name
            )

        return

    # =====================================================
    # Other operations
    # =====================================================

    column = calculation.get(
        "column"
    )

    if column not in columns:

        raise ValueError(
            f"Invalid column: {column}"
        )

    if operation == "GROUP_BY":

        group_by = calculation.get(
            "group_by"
        )

        if not group_by:

            raise ValueError(
                "GROUP_BY requires group_by"
            )

        if group_by not in columns:

            raise ValueError(
                f"Invalid group_by column: {group_by}"
            )


# =========================================================
# GROUP_BY_METRICS executor
# =========================================================


def execute_group_by_metrics(
    dataframe: pd.DataFrame,
    calculation: dict
):

    group_by = calculation[
        "group_by"
    ]

    metrics = calculation[
        "metrics"
    ]

    derived_items = (
        calculation.get(
            "derived",
            []
        )
    )

    result_dataframe = None

    # -----------------------------------------------------
    # Calculate every requested metric
    # -----------------------------------------------------

    for metric in metrics:

        column = metric[
            "column"
        ]

        alias = metric[
            "alias"
        ]

        metric_dataframe = dataframe[
            [
                group_by,
                column
            ]
        ].copy()

        metric_dataframe[
            column
        ] = pd.to_numeric(
            metric_dataframe[
                column
            ],
            errors="coerce"
        )

        metric_dataframe = (
            metric_dataframe
            .dropna(
                subset=[
                    group_by,
                    column
                ]
            )
        )

        metric_dataframe = (
            metric_dataframe
            .groupby(
                group_by,
                as_index=False
            )[column]
            .sum()
        )

        metric_dataframe = (
            metric_dataframe.rename(
                columns={
                    column: alias
                }
            )
        )

        if result_dataframe is None:

            result_dataframe = (
                metric_dataframe
            )

        else:

            result_dataframe = (
                result_dataframe.merge(
                    metric_dataframe,
                    on=group_by,
                    how="outer"
                )
            )

    if result_dataframe is None:

        result_dataframe = (
            pd.DataFrame(
                columns=[
                    group_by
                ]
            )
        )

    # -----------------------------------------------------
    # Replace missing metric values with 0
    # -----------------------------------------------------

    for metric in metrics:

        alias = metric[
            "alias"
        ]

        if (
            alias
            in result_dataframe.columns
        ):

            result_dataframe[
                alias
            ] = (
                result_dataframe[
                    alias
                ]
                .fillna(0)
            )

    # -----------------------------------------------------
    # Derived columns
    # -----------------------------------------------------

    for derived in derived_items:

        name = derived[
            "name"
        ]

        operation = derived[
            "operation"
        ]

        left = derived[
            "left"
        ]

        right = derived[
            "right"
        ]

        if operation == "SUBTRACT":

            result_dataframe[
                name
            ] = (
                result_dataframe[
                    left
                ]
                -
                result_dataframe[
                    right
                ]
            )

    # -----------------------------------------------------
    # Optional sorting
    # -----------------------------------------------------

    sort_by = calculation.get(
        "sort_by"
    )

    sort_direction = (
        calculation.get(
            "sort",
            "DESC"
        )
    )

    if (
        sort_by
        and
        sort_by
        in result_dataframe.columns
    ):

        result_dataframe = (
            result_dataframe.sort_values(
                by=sort_by,
                ascending=(
                    str(
                        sort_direction
                    ).upper()
                    == "ASC"
                )
            )
        )

    # -----------------------------------------------------
    # Optional limit
    # -----------------------------------------------------

    limit = calculation.get(
        "limit"
    )

    if limit is not None:

        result_dataframe = (
            result_dataframe.head(
                int(limit)
            )
        )

    return result_dataframe


# =========================================================
# Main calculation executor
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

    operation = (
        calculation[
            "operation"
        ]
    )

    sheet_name = (
        calculation[
            "sheet"
        ]
    )

    dataframe = sheets[
        sheet_name
    ]

    filters = calculation.get(
        "filters",
        []
    )

    # -----------------------------------------------------
    # Apply filters BEFORE calculation
    # -----------------------------------------------------

    dataframe = apply_filters(
        dataframe=dataframe,
        filters=filters
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
        len(dataframe)
    )

    print(
        "==================================="
    )

    result = {
        "id": calculation_id,
        "operation": operation,
        "sheet": sheet_name,
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

            normalized_record = {}

            for key, value in record.items():

                normalized_record[
                    key
                ] = normalize_value(
                    value
                )

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

    # -----------------------------------------------------
    # From here onwards operations have column
    # -----------------------------------------------------

    column = calculation[
        "column"
    ]

    result[
        "column"
    ] = column

    # =====================================================
    # SUM
    # =====================================================

    if operation == "SUM":

        result[
            "value"
        ] = normalize_value(
            calculate_sum(
                dataframe,
                column
            )
        )

        return result

    # =====================================================
    # AVERAGE
    # =====================================================

    if operation == "AVERAGE":

        result[
            "value"
        ] = normalize_value(
            calculate_average(
                dataframe,
                column
            )
        )

        return result

    # =====================================================
    # MIN
    # =====================================================

    if operation == "MIN":

        result[
            "value"
        ] = normalize_value(
            calculate_min(
                dataframe,
                column
            )
        )

        return result

    # =====================================================
    # MAX
    # =====================================================

    if operation == "MAX":

        result[
            "value"
        ] = normalize_value(
            calculate_max(
                dataframe,
                column
            )
        )

        return result

    # =====================================================
    # COUNT
    # =====================================================

    if operation == "COUNT":

        result[
            "value"
        ] = normalize_value(
            calculate_count(
                dataframe,
                column
            )
        )

        return result

    # =====================================================
    # GROUP_BY
    # =====================================================

    if operation == "GROUP_BY":

        group_by = calculation[
            "group_by"
        ]

        aggregation = (
            calculation.get(
                "aggregation",
                "SUM"
            )
        )

        sort = calculation.get(
            "sort",
            "DESC"
        )

        limit = calculation.get(
            "limit"
        )

        grouped_dataframe = (
            calculate_grouped_sum(
                dataframe=dataframe,
                group_by=group_by,
                column=column,
                sort=sort,
                limit=limit
            )
        )

        records = (
            grouped_dataframe
            .to_dict(
                orient="records"
            )
        )

        normalized_records = []

        for record in records:

            normalized_records.append({
                group_by:
                    normalize_value(
                        record[
                            group_by
                        ]
                    ),

                column:
                    normalize_value(
                        record[
                            column
                        ]
                    )
            })

        result[
            "group_by"
        ] = group_by

        result[
            "aggregation"
        ] = aggregation

        result[
            "sort"
        ] = sort

        result[
            "limit"
        ] = limit

        result[
            "rows"
        ] = normalized_records

        # Only expose group/value when exactly
        # one grouped row is returned.
        if (
            len(
                normalized_records
            )
            == 1
        ):

            result[
                "group"
            ] = (
                normalized_records[
                    0
                ][
                    group_by
                ]
            )

            result[
                "value"
            ] = (
                normalized_records[
                    0
                ][
                    column
                ]
            )

        return result

    raise ValueError(
        f"Operation not implemented: {operation}"
    )