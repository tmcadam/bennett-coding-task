from typing import Any, cast

import requests

from custom_errors import BNFCodeNotFoundError
from custom_types import OrgDetailEntry, SpendingByOrgEntry, BNFCodeEntry


class OpenPrescribingClient:
    BASE_URL = "https://openprescribing.net/api/1.0"

    def __init__(self, user_agent: str, timeout: int = 10) -> None:
        self.user_agent: str = user_agent
        self.headers: dict[str, str] = {"User-Agent": self.user_agent}
        self.timeout: int = timeout

    def fetch_data_from_api(
        self, resource: str, params: dict[str, str | bool]
    ) -> list[dict[str, Any]]:
        """Fetch data from the OpenPrescribing API.

        Args:
            resource (str): The API resource endpoint.
            params (dict): The query parameters for the API request.
            headers (dict): The headers for the API request.

        Returns:
            list[dict]: The JSON response from the API as a list of dictionaries.

        Raises:
            RequestException: If the API request fails due to network issues or other reasons.
        """
        response: requests.Response = requests.get(
            f"{self.BASE_URL}/{resource}/",
            params=params,
            headers=self.headers,
            timeout=self.timeout,
        )
        response.raise_for_status()
        json_data: list[dict[str, Any]] = response.json()
        return json_data

    def fetch_chemical_name(self, bnf_code: str) -> str:
        """Fetch the chemical name for a given BNF code from the OpenPrescribing API.

        Args:
            bnf_code (str): The BNF code for which to fetch the chemical name.

        Side Effects:
            Raises a BNFCodeNotFoundError if the BNF code is not found in the OpenPrescribing API
            or if the response does not contain a chemical name field.

            Raises a RequestException if the API request fails due to network issues or other reasons.

        Returns:
            str: The chemical name if found
        """

        params: dict[str, str | bool] = {"exact": True, "format": "json", "q": bnf_code}

        # Check if the response contains data for the given BNF code
        data: list[BNFCodeEntry] = cast(
            list[BNFCodeEntry], self.fetch_data_from_api("bnf_code", params)
        )

        if not data:
            raise BNFCodeNotFoundError(
                f"No chemical information found for BNF code {bnf_code}"
            )

        # Return the chemical name from the first entry in the response data
        chemical_name: str = data[0]["name"]

        return chemical_name

    def fetch_icb_spending_data(self, bnf_code: str) -> list[SpendingByOrgEntry]:
        """Fetch ICB spending data for a given BNF code from the OpenPrescribing API."""

        params: dict[str, str | bool] = {
            "format": "json",
            "code": bnf_code,
            "org_type": "icb",
        }

        spending_data: list[SpendingByOrgEntry] = cast(
            list[SpendingByOrgEntry],
            self.fetch_data_from_api("spending_by_org", params),
        )
        if not spending_data:
            raise BNFCodeNotFoundError(
                f"No spending data found for BNF code {bnf_code}"
            )

        return spending_data

    def fetch_organisation_data(self) -> list[OrgDetailEntry]:
        """Fetch organisation information for ICBs from the OpenPrescribing API."""

        params: dict[str, str | bool] = {
            "format": "json",
            "org_type": "icb",
            "keys": "total_list_size",
        }

        org_data: list[OrgDetailEntry] = cast(
            list[OrgDetailEntry], self.fetch_data_from_api("org_details", params)
        )
        if not org_data:
            raise BNFCodeNotFoundError("No organisation data found")

        return org_data
