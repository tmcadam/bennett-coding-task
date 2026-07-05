"""OpenPrescribing CLI

This module provides a command-line interface (CLI) for interacting with the OpenPrescribing API.
"""

import os

import requests
import click

from custom_errors import MissingUserAgentError, InvalidBNFCodeError, BNFCodeNotFoundError


def get_user_agent() -> str | None:
    """Retrieve the user agent string from the environment variable.

    Returns:
        str | None: The user agent string or None if not set.

    """
    return os.environ.get("OPENPRESCRIBING_USER_AGENT", None)


def valid_bnf_code(bnf_code: str) -> bool:
    """Valid BNF code format: must be 15 characters.

    Args:
        bnf_code (str): The BNF code to validate.

    Returns:
        bool: True if the BNF code is valid, False otherwise.
    """

    return len(bnf_code) == 15


def lookup_chemical_name(bnf_code: str, user_agent: str) -> str | None:
    """Fetch the chemical name for a given BNF code from the OpenPrescribing API.

    Args:
        bnf_code (str): The BNF code for which to fetch the chemical name.
        user_agent (str | None): The user agent string to use for the API request.

    Returns:
        str | None: The chemical name if found, otherwise None.
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
        raise BNFCodeNotFoundError(f"No data found for BNF code {bnf_code}")

    # Return the chemical name from the first entry in the response data
    chemical_name: str | None = data[0].get("name", None)

    return chemical_name


@click.command()
@click.argument("bnf_code", type=str)
def main(bnf_code: str) -> None:
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

        chemical_name: str | None = lookup_chemical_name(bnf_code, user_agent)
        if not chemical_name:
            exit(f"Error: Could not fetch chemical name for BNF code {bnf_code}")

        # Print the chemical name to the console
        print(f"\n{chemical_name}\n")

    except requests.exceptions.RequestException:
        exit("Error: Failed to fetch data from OpenPrescribing API")

    except Exception as e:
        exit(f"Error: {e}")


if __name__ == "__main__":
    main()
