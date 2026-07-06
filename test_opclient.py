import pytest
from requests import HTTPError, RequestException

from opclient import OpenPrescribingClient
from custom_errors import BNFCodeNotFoundError


class TestOpenPrescribingAPI:
    def test_fetch_data_from_api_returns_expected_value(self, mocker):
        r = mocker.Mock()
        r.status_code = 200
        r.json.return_value = [{"key": "value"}]
        mocker.patch("opclient.requests.get", return_value=r)

        user_agent = "test-user-agent"
        resource = "bnf_code"
        params = {"exact": True, "format": "json", "q": "123456789012345"}

        client = OpenPrescribingClient(user_agent=user_agent)
        data = client.fetch_data_from_api(resource, params)
        assert data == [{"key": "value"}]

    def test_fetch_data_from_api_raises_RequestException_for_status_code_gt_400(
        self, mocker
    ):
        r = mocker.Mock()
        r.status_code = 404
        r.raise_for_status.side_effect = HTTPError("404 Not Found")
        mocker.patch("opclient.requests.get", return_value=r)

        user_agent = "test-user-agent"
        resource = "bnf_code"
        params = {"exact": True, "format": "json", "q": "123456789012345"}

        client = OpenPrescribingClient(user_agent=user_agent)
        with pytest.raises(RequestException):
            client.fetch_data_from_api(resource, params)


class TestFetchChemicalName:
    def test_fetch_chemical_name_returns_expected_value(self, mocker):
        r = mocker.Mock()
        r.status_code = 200
        r.json.return_value = [{"name": "Test Chemical Name"}]
        mocker.patch("opclient.requests.get", return_value=r)

        bnf_code = "123456789012345"
        user_agent = "test-user-agent"
        expected_chemical_name = "Test Chemical Name"

        client = OpenPrescribingClient(user_agent=user_agent)
        chemical_name = client.fetch_chemical_name(bnf_code)
        assert chemical_name == expected_chemical_name

    def test_fetch_chemical_name_raises_BNFCodeNotFoundError_for_not_found(
        self, mocker
    ):
        r = mocker.Mock()
        r.status_code = 200
        r.json.return_value = []
        mocker.patch("opclient.requests.get", return_value=r)

        bnf_code = "123456789012345"
        user_agent = "test-user-agent"

        client = OpenPrescribingClient(user_agent=user_agent)
        with pytest.raises(BNFCodeNotFoundError):
            client.fetch_chemical_name(bnf_code)


class TestFetchICBSpendingData:
    def test_fetch_icb_spending_data_returns_expected_value(self, mocker):
        r = mocker.Mock()
        r.status_code = 200
        r.json.return_value = [
            {"date": "2023-01", "row_name": "ICB A", "items": 100},
            {"date": "2023-01", "row_name": "ICB B", "items": 150},
        ]
        mocker.patch("opclient.requests.get", return_value=r)

        bnf_code = "123456789012345"
        user_agent = "test-user-agent"
        expected_spending_data = [
            {"date": "2023-01", "row_name": "ICB A", "items": 100},
            {"date": "2023-01", "row_name": "ICB B", "items": 150},
        ]

        client = OpenPrescribingClient(user_agent=user_agent)
        spending_data = client.fetch_icb_spending_data(bnf_code)
        assert spending_data == expected_spending_data

    def test_fetch_icb_spending_data_raises_BNFCodeNotFoundError_for_no_data(
        self, mocker
    ):
        r = mocker.Mock()
        r.status_code = 200
        r.json.return_value = []
        mocker.patch("opclient.requests.get", return_value=r)

        bnf_code = "123456789012345"
        user_agent = "test-user-agent"

        client = OpenPrescribingClient(user_agent=user_agent)
        with pytest.raises(BNFCodeNotFoundError):
            client.fetch_icb_spending_data(bnf_code)
