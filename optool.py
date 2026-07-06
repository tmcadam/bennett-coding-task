"""OpenPrescribing CLI

This module provides a command-line interface (CLI) for interacting with the OpenPrescribing API.
"""

import os

import requests
import click

from custom_types import (
    MonthlyICBSummary,
    MonthlyICBStats,
    OrgDetailEntry,
    SpendingByOrgEntry,
)
from custom_errors import (
    MissingUserAgentError,
    InvalidBNFCodeError,
)

from opclient import OpenPrescribingClient


def get_user_agent() -> str | None:
    """Retrieve the user agent string from the environment variable.

    Returns:
        str | None: The user agent string or None if not set.

    """
    return os.environ.get("OPENPRESCRIBING_USER_AGENT", None)


def valid_bnf_code(bnf_code: str) -> bool:
    """Valid BNF code format:
        - must be 15 characters long

    Args:
        bnf_code (str): The BNF code to check for validity

    Returns:
        bool: True if the BNF code is valid, False otherwise.
    """
    return len(bnf_code) == 15


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


@click.command()
@click.argument("bnf_code", type=str)
@click.option(
    "--weighted",
    is_flag=True,
    help="Calculate patient weighted spending for the given BNF code",
)
def main(bnf_code: str, weighted: bool | None) -> None:
    """Process a target file and extract metrics.

    BNF_CODE is the 15-character BNF code for which to fetch the chemical name.
    """

    try:
        user_agent: str | None = get_user_agent()
        if not user_agent:
            raise MissingUserAgentError(
                "OPENPRESCRIBING_USER_AGENT environment variable is not set."
            )

        client = OpenPrescribingClient(user_agent=user_agent)

        if not valid_bnf_code(bnf_code):
            raise InvalidBNFCodeError(
                f"BNF code must be 15 characters long. Provided code: {bnf_code}"
            )

        chemical_name: str = client.fetch_chemical_name(bnf_code)

        spending_data: list[SpendingByOrgEntry] = client.fetch_icb_spending_data(
            bnf_code
        )

        top_spending_data: list[MonthlyICBSummary]
        if weighted:
            # Fetch organization data to get total list size for each ICB
            organisation_data = client.fetch_organisation_data()
            # Calculate patient weighted spending
            top_spending_data = top_monthly_prescribing_icbs_by_items_per_patient(
                spending_data, organisation_data
            )

        else:
            # Calculate top spending ICBs without weighting
            top_spending_data = top_monthly_prescribing_icbs_by_total_items(
                spending_data
            )

        # Print the chemical name to the console
        print(f"\n{chemical_name}\n")

        # Print the top spending ICB for each month to the console
        for entry in top_spending_data:
            print(f"{entry['month']} {entry['icb']}")

    except requests.exceptions.RequestException:
        exit("Error: Failed to fetch data from OpenPrescribing API")

    except Exception as e:
        exit(f"Error: {e}")


if __name__ == "__main__":
    main()
