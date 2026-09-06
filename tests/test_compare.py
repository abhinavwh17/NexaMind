import pytest

from app.services.calculation_service import execute_result_calculation


def test_compare_calculates_difference_and_percentage_change():
    previous_results = [
        {
            "id": "calc_1",
            "operation": "SUM",
            "value": 100.0,
        },
        {
            "id": "calc_2",
            "operation": "SUM",
            "value": 150.0,
        },
    ]

    calculation = {
        "id": "calc_3",
        "operation": "COMPARE",
        "left": {
            "calculation_id": "calc_1",
            "field": "value",
        },
        "right": {
            "calculation_id": "calc_2",
            "field": "value",
        },
    }

    result = execute_result_calculation(
        calculation=calculation,
        calculation_results=previous_results,
    )

    assert result["left_value"] == 100.0
    assert result["right_value"] == 150.0
    assert result["difference"] == 50.0
    assert result["absolute_difference"] == 50.0
    assert result["percentage_change"] == pytest.approx(50.0)
    assert result["direction"] == "increase"


def test_compare_handles_zero_left_value():
    previous_results = [
        {
            "id": "calc_1",
            "operation": "SUM",
            "value": 0.0,
        },
        {
            "id": "calc_2",
            "operation": "SUM",
            "value": 50.0,
        },
    ]

    calculation = {
        "id": "calc_3",
        "operation": "COMPARE",
        "left": {
            "calculation_id": "calc_1",
            "field": "value",
        },
        "right": {
            "calculation_id": "calc_2",
            "field": "value",
        },
    }

    result = execute_result_calculation(
        calculation=calculation,
        calculation_results=previous_results,
    )

    assert result["difference"] == 50.0
    assert result["percentage_change"] is None
    assert result["direction"] == "increase"
