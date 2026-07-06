from custom_types import (
    MonthlyICBStats,
    MonthlyICBSummary,
    OrgDetailEntry,
    SpendingByOrgEntry,
)


def top_monthly_prescribing_icbs(
    spending_data: list[SpendingByOrgEntry],
    patient_count_data: dict[tuple[str, str], int] | None = None,
) -> list[MonthlyICBSummary]:
    """Parse monthly ICB spending data to identify the ICB with the highest item measure per month.

    For each month in the spending data the item count is used as the measure.

    The function returns a list of dictionaries mapping each month to the ICB that had the
    highest measure for that month, along with the corresponding measure value.

    Args:
        spending_data: A list of dictionaries, each representing a spending entry with
            keys "date" (month string), "row_name" (ICB name), and "items"
            (number of items).
        patient_count_data: A dictionary mapping (month, ICB) tuples to patient counts.
    Returns:
        A list of dictionaries mapping month strings to dictionaries with keys:
            - "icb" (str): The name of the ICB with the highest measure for that month.
    """

    # data structure to hold the highest ICB for each month
    highest_icb_monthly: dict[str, MonthlyICBStats] = {}

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
        highest_icb = highest_icb_monthly.get(month, None)

        # check if the current ICB has a higher measure than the current maximum for this month
        if not highest_icb or measure > highest_icb["measure"]:
            highest_icb_monthly[month] = {"icb": icb, "measure": measure}

    returned_data: list[MonthlyICBSummary] = [
        {"month": month, "icb": data["icb"]}
        for month, data in highest_icb_monthly.items()
    ]
    returned_data.sort(
        key=lambda x: x["month"], reverse=False
    )  # Sort by month in ascending order

    return returned_data


def top_monthly_prescribing_icbs_by_total_items(
    spending_data: list[SpendingByOrgEntry],
) -> list[MonthlyICBSummary]:

    return top_monthly_prescribing_icbs(spending_data)


def top_monthly_prescribing_icbs_by_items_per_patient(
    spending_data: list[SpendingByOrgEntry], organization_data: list[OrgDetailEntry]
) -> list[MonthlyICBSummary]:

    # Create a lookup dictionary for patient count data
    patient_count_data: dict[tuple[str, str], int] = {
        (item["date"], item["row_name"]): item["total_list_size"]
        for item in organization_data
    }

    # Call the ranking function with the patient count data
    return top_monthly_prescribing_icbs(spending_data, patient_count_data)
