"""OpenPrescribing CLI

This module provides a command-line interface (CLI) for interacting with the OpenPrescribing API.
"""

import os

import requests
import click

from custom_types import SpendingEntry, MonthlyICBSummary, MonthlyICBStats, OrganizationEntry
from custom_errors import (
    MissingUserAgentError,
    InvalidBNFCodeError,
    BNFCodeNotFoundError,
)


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
    spending_data: list[SpendingEntry],
    patient_count_data: list[OrganizationEntry] | None = None
) -> list[MonthlyICBSummary]:
    """Parse monthly ICB spending data to identify the ICB with the highest item measure per month.

    For each month in the spending data the item count is used as the measure.

    The function returns a list of dictionaries mapping each month to the ICB that had the
    highest measure for that month, along with the corresponding measure value.

    Args:
        spending_data: A list of dictionaries, each representing a spending entry with
            keys "date" (month string), "row_name" (ICB name), and "items"
            (number of items).
        patient_count_data: A list of dictionaries containing patient count data with
            keys "date", "row_name", and "total_list_size".
    Returns:
        A list of dictionaries mapping month strings to dictionaries with keys:
            - "icb" (str): The name of the ICB with the highest measure for that month.
    """

    # data structure to hold the highest ICB for each month
    highest_icb_monthly: dict[str, MonthlyICBStats] = {}

    for entry in spending_data:
        month: str = entry["date"]
        icb: str = entry["row_name"]
        if patient_count_data:
            # If patient count data is provided, calculate the measure as items divided by the patient count for that ICB and month.
            measure: float = entry["items"] / patient_count_data[(month, icb)]
        else:
            # If patient count data is not provided, use the raw item count as the measure
            measure: int = entry["items"]

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


def top_monthly_prescribing_icbs_by_total_items(spending_data: list[SpendingEntry]) -> list[MonthlyICBSummary]:

    return top_monthly_prescribing_icbs(spending_data)


def top_monthly_prescribing_icbs_by_items_per_patient(
    spending_data: list[SpendingEntry], organization_data: list[OrganizationEntry]
) -> list[MonthlyICBSummary]:

    # Create a lookup dictionary for patient count data
    patient_count_data: dict[tuple[str, str], int] = {
        (item["date"], item["row_name"]): item["total_list_size"]
        for item in organization_data
    }

    # Call the ranking function with the patient count data
    return top_monthly_prescribing_icbs(
        spending_data, patient_count_data
    )


def lookup_chemical_name(bnf_code: str, user_agent: str) -> str:
    """Fetch the chemical name for a given BNF code from the OpenPrescribing API.

    Args:
        bnf_code (str): The BNF code for which to fetch the chemical name.
        user_agent (str | None): The user agent string to use for the API request.

    Returns:
        str: The chemical name if found
    """

    url: str = "https://openprescribing.net/api/1.0/bnf_code/"
    params: dict[str, str | bool] = {"exact": True, "format": "json", "q": bnf_code}
    headers: dict[str, str] = {"User-Agent": user_agent}

    # Make the API request with a timeout to avoid hanging indefinitely
    response: requests.Response = requests.get(
        url, headers=headers, params=params, timeout=10
    )
    response.raise_for_status()

    # Check if the response contains data for the given BNF code
    data: list[dict[str, str]] = response.json()
    if not data:
        raise BNFCodeNotFoundError(
            f"No chemical information found for BNF code {bnf_code}"
        )

    # Return the chemical name from the first entry in the response data
    chemical_name: str | None = data[0].get("name", None)
    if not chemical_name:
        raise BNFCodeNotFoundError(
            f"No chemical name found in response for BNF code {bnf_code}"
        )

    return chemical_name


def fetch_icb_spending_data(bnf_code: str, user_agent: str) -> list[SpendingEntry]:
    """Fetch ICB spending data for a given BNF code from the OpenPrescribing API."""

    params: dict[str, str | bool] = {
        "format": "json",
        "code": bnf_code,
        "org_type": "icb",
    }
    headers: dict[str, str] = {"User-Agent": user_agent}

    response = requests.get(
        "https://openprescribing.net/api/1.0/spending_by_org/",
        params=params,
        headers=headers,
    )
    response.raise_for_status()

    spending_data: list[SpendingEntry] = response.json()
    if not spending_data:
        raise BNFCodeNotFoundError(f"No spending data found for BNF code {bnf_code}")

    return spending_data

def fetch_organization_data(user_agent: str) -> list[OrganizationEntry]:
    """Fetch organization information for ICBs from the OpenPrescribing API."""

    params: dict[str, str | bool] = {
        "format": "json",
        "org_type": "icb",
        "keys": "total_list_size",
    }
    headers: dict[str, str] = {"User-Agent": user_agent}

    response = requests.get(
        "https://openprescribing.net/api/1.0/org_details/",
        params=params,
        headers=headers,
        timeout=10  # Set a timeout to avoid hanging indefinitely
    )
    response.raise_for_status()

    org_data: list[OrganizationEntry] = response.json()
    if not org_data:
        raise BNFCodeNotFoundError("No organization data found")

    return org_data

@click.command()
@click.argument("bnf_code", type=str)
@click.option("--weighted", is_flag=True, help="Calculate patient weighted spending for the given BNF code")
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

        if not valid_bnf_code(bnf_code):
            raise InvalidBNFCodeError(
                f"BNF code must be 15 characters long. Provided code: {bnf_code}"
            )

        chemical_name: str = lookup_chemical_name(bnf_code, user_agent)

        spending_data: list[SpendingEntry] = fetch_icb_spending_data(
            bnf_code, user_agent
        )

        if weighted:
            # Fetch organization data to get total list size for each ICB
            organization_data: list[OrganizationEntry] = fetch_organization_data(user_agent)

            # Calculate patient weighted spending
            top_spending_data = top_monthly_prescribing_icbs_by_items_per_patient(spending_data, organization_data)

        else:
            # Calculate top spending ICBs without weighting
            top_spending_data: list[MonthlyICBSummary] = top_monthly_prescribing_icbs_by_total_items(
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
