"""OpenPrescribing CLI

This module provides a command-line interface (CLI) for interacting with the OpenPrescribing API.
"""

import requests
import click

from custom_types import (
    MonthlyTopPrescribingICB,
    SpendingByOrgEntry,
)

from opclient import OpenPrescribingClient
from opsummary import (
    top_monthly_prescribing_icbs_by_total_items,
    top_monthly_prescribing_icbs_by_items_per_patient,
)


class InvalidBNFCodeError(Exception):
    """Custom exception raised when an invalid BNF code is provided."""

    pass


def valid_bnf_code(bnf_code: str) -> bool:
    """Valid BNF code format:
        - must be 15 characters long

    Args:
        bnf_code (str): The BNF code to check for validity

    Returns:
        bool: True if the BNF code is valid, False otherwise.
    """
    return len(bnf_code) == 15


@click.command()
@click.argument("bnf_code", type=str)
@click.option(
    "--weighted",
    is_flag=True,
    help="Use patient weighted spending to determine the top prescribing ICBs",
)
@click.option(
    "--user-agent",
    type=str,
    default=None,
    help="User agent string for API requests",
)
def main(bnf_code: str, weighted: bool | None, user_agent: str | None) -> None:
    """Look up the chemical name and top prescribing ICBs for a given BNF code from the OpenPrescribing API.

    BNF_CODE is the 15-character BNF code for which to fetch the chemical name.
    """

    try:
        client = OpenPrescribingClient(user_agent=user_agent)

        if not valid_bnf_code(bnf_code):
            raise InvalidBNFCodeError(
                f"BNF code must be 15 characters long. Provided code: {bnf_code}"
            )

        chemical_name: str = client.fetch_chemical_name(bnf_code)

        spending_data: list[SpendingByOrgEntry] = client.fetch_icb_spending_data(
            bnf_code
        )

        top_spending_data: list[MonthlyTopPrescribingICB]
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
        print("\n")

    except requests.exceptions.RequestException:
        exit("Error: Failed to fetch data from OpenPrescribing API")

    except Exception as e:
        exit(f"Error: {e}")


if __name__ == "__main__":
    main()
