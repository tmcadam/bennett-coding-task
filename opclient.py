from typing import Any, cast

import requests

from custom_types import OrgDetailEntry, SpendingByOrgEntry, BNFCodeEntry


class BNFCodeNotFoundError(Exception):
    """Custom exception raised when a BNF code is not found in the OpenPrescribing API."""

    pass


class OrgDataNotFoundError(Exception):
    """Custom exception raised when organisation data is not found in the OpenPrescribing API."""

    pass


class OpenPrescribingClient:
    """Client for interacting with the OpenPrescribing API.

    This client provides methods to fetch BNF code information, ICB spending data,
    and organisation data from the OpenPrescribing API.

    Attributes:
        BASE_URL: The base URL for the OpenPrescribing API.
        user_agent: The User-Agent header value for API requests.
        headers: The HTTP headers to include in API requests.
        timeout: The timeout in seconds for API requests.
    """

    BASE_URL = "https://openprescribing.net/api/1.0"

    def __init__(self, user_agent: str | None, timeout: int = 10) -> None:
        """Initialize the OpenPrescribingClient.

        Args:
            user_agent: The User-Agent header value for API requests. If None, no User-Agent header will be sent.
            timeout: The timeout in seconds for API requests. Defaults to 10.
        """
        self.user_agent: str | None = user_agent
        self.headers: dict[str, str] = (
            {"User-Agent": self.user_agent} if self.user_agent else {}
        )
        self.timeout: int = timeout

    def fetch_data_from_api(
        self, resource: str, params: dict[str, str | bool]
    ) -> list[dict[str, Any]]:
        """Fetch data from the OpenPrescribing API.

        Args:
            resource: The API resource endpoint (e.g., "bnf_code", "spending_by_org", "org_details").
            params: The query parameters for the API request.

        Returns:
            A list of dictionaries containing the JSON response from the API.

        Raises:
            requests.RequestException: If the API request fails due to network issues, HTTP errors, or other reasons.
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
            bnf_code: The BNF code (e.g., "1002108AA00") for which to fetch the chemical name.

        Returns:
            The chemical name associated with the given BNF code.

        Raises:
            BNFCodeNotFoundError: If the BNF code is not found in the OpenPrescribing API
                or if the response does not contain a chemical name field.
            requests.RequestException: If the API request fails due to network issues or other reasons.
        """

        params: dict[str, str | bool] = {"format": "json", "q": bnf_code}

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
        """Fetch ICB spending data for a given BNF code from the OpenPrescribing API.

        Args:
            bnf_code: The BNF code for which to fetch spending data.

        Returns:
            A list of SpendingByOrgEntry dictionaries containing spending data for the given BNF code,
            with keys "date", "row_name", and "items".

        Raises:
            BNFCodeNotFoundError: If no spending data is found for the given BNF code.
            requests.RequestException: If the API request fails due to network issues or other reasons.
        """

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
        """Fetch organisation information for ICBs from the OpenPrescribing API.

        Returns:
            A list of OrgDetailEntry dictionaries containing organisation data for ICBs,
            with keys "date", "row_name", and "total_list_size".

        Raises:
            OrgDataNotFoundError: If no organisation data is found in the API response.
            requests.RequestException: If the API request fails due to network issues or other reasons.
        """

        params: dict[str, str | bool] = {
            "format": "json",
            "org_type": "icb",
            "keys": "total_list_size",
        }

        org_data: list[OrgDetailEntry] = cast(
            list[OrgDetailEntry], self.fetch_data_from_api("org_details", params)
        )
        if not org_data:
            raise OrgDataNotFoundError("No organisation data found")

        return org_data
