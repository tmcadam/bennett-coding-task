"""
This module provides functions to analyse monthly prescribing data for Integrated Care Boards (ICBs)
and identify the ICB with the highest prescribing measure for each month.

It has two main functions:

1. top_monthly_prescribing_icbs_by_total_items: Identifies the ICB with the highest total items
prescribed for each month.

2. top_monthly_prescribing_icbs_by_items_per_patient: Identifies the ICB with the highest items
prescribed per patient for each month, using patient count data.

The module uses custom types defined in custom_types.py for type hinting and data structure definitions.
"""

from custom_types import (
    MonthlyICBStats,
    MonthlyTopPrescribingICB,
    OrgDetailEntry,
    SpendingByOrgEntry,
)


def _top_monthly_prescribing_icbs(
    spending_data: list[SpendingByOrgEntry],
    patient_count_data: dict[tuple[str, str], int] | None = None,
) -> list[MonthlyTopPrescribingICB]:
    """Rank the highest-prescribing ICB for each month.

    This helper compares each month's spending entries and keeps the ICB with the highest
    measure for that month. When patient counts are provided, the measure is calculated as
    items per patient; otherwise it uses the raw item count.

    Args:
        spending_data: Spending entries for each ICB and month.
        patient_count_data: Optional mapping of (month, ICB) to patient counts used to
            calculate a per-patient measure.

    Returns:
        A list of monthly summaries, where each entry contains the month and the selected ICB.
    """

    # data structure to hold the highest ICB for each month
    top_monthly_prescribing_icbs_tmp: dict[str, MonthlyICBStats] = {}

    for entry in spending_data:
        month: str = entry["date"]
        icb: str = entry["row_name"]
        measure: int | float
        if patient_count_data:
            # If patient count data is provided, calculate the measure as items divided by the patient count for that ICB and month.
            measure = entry["items"] / patient_count_data[(month, icb)]
        else:
            # If patient count data is not provided, use the raw item count as the measure
            measure = entry["items"]

        # lookup the current maximum items for this month, if any
        top_icb = top_monthly_prescribing_icbs_tmp.get(month, None)

        # check if the current ICB has a higher measure than the current maximum for this month
        if not top_icb or measure > top_icb["measure"]:
            top_monthly_prescribing_icbs_tmp[month] = {"icb": icb, "measure": measure}

    # Convert the dictionary to a list of MonthlyTopPrescribingICB entries
    top_monthly_prescribing_icbs: list[MonthlyTopPrescribingICB] = [
        {"month": month, "icb": data["icb"]}
        for month, data in top_monthly_prescribing_icbs_tmp.items()
    ]
    # Sort by month in ascending order
    top_monthly_prescribing_icbs.sort(
        key=lambda x: x["month"], reverse=False
    )

    return top_monthly_prescribing_icbs


def top_monthly_prescribing_icbs_by_total_items(
    spending_data: list[SpendingByOrgEntry],
) -> list[MonthlyTopPrescribingICB]:
    """Rank the highest-prescribing ICB for each month based on total items.

    This function identifies the ICB with the highest total item count for each month
    using the provided spending data.

    Args:
        spending_data: A list of SpendingByOrgEntry dictionaries containing the spending data for each ICB and month, with keys "date", "row_name", and "items".

    Returns:
        A list of MonthlyTopPrescribingICB entries, each containing the month and the ICB with the highest total items for that month, sorted by month in ascending order.
    """

    return _top_monthly_prescribing_icbs(spending_data, None)


def top_monthly_prescribing_icbs_by_items_per_patient(
    spending_data: list[SpendingByOrgEntry], organization_data: list[OrgDetailEntry]
) -> list[MonthlyTopPrescribingICB]:
    """Rank the highest-prescribing ICB for each month based on items per patient.

    This function calculates the items per patient for each ICB and month using the provided
    spending data and organization data, and then identifies the ICB with the highest items
    per patient for each month.

    Args:
        spending_data: A list of SpendingByOrgEntry dictionaries containing the spending data for each ICB and month, with keys "date", "row_name", and "items".
        organization_data: A list of OrgDetailEntry dictionaries containing the patient count data for each ICB and month, with keys "date", "row_name", and "total_list_size".

    Returns:
        A list of MonthlyTopPrescribingICB entries, each containing the month and the ICB with the highest items per patient for that month, sorted by month in ascending order.
    """

    # Create dictionary for fast O(1) lookup of patient count data
    patient_count_data: dict[tuple[str, str], int] = {
        (item["date"], item["row_name"]): item["total_list_size"]
        for item in organization_data
    }

    # Call the ranking function with the spending_data and patient count data
    return _top_monthly_prescribing_icbs(spending_data, patient_count_data)
