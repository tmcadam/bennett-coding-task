import pytest
from requests.exceptions import RequestException, HTTPError
from click.testing import CliRunner

from optool import (
    top_monthly_icb_spending,
    main,
    get_user_agent,
    valid_bnf_code,
    lookup_chemical_name,
    fetch_icb_spending_data,
    BNFCodeNotFoundError,
)


class TestGetUserAgent:
    def test_get_user_agent_returns_expected_value(self, monkeypatch):
        # Set the environment variable for testing
        monkeypatch.setenv("OPENPRESCRIBING_USER_AGENT", "test-user-agent")

        assert get_user_agent() == "test-user-agent"

    def test_get_user_agent_returns_none_when_not_set(self, monkeypatch):
        # Unset the environment variable for testing
        monkeypatch.delenv("OPENPRESCRIBING_USER_AGENT", raising=False)

        assert get_user_agent() is None


class TestValidBNFCode:
    def test_valid_bnf_code_returns_true_for_valid_code(self):
        assert valid_bnf_code("123456789012345") is True

    def test_valid_bnf_code_returns_false_for_invalid_code(self):
        assert valid_bnf_code("12345") is False
        assert valid_bnf_code("1234567890123456") is False


class TestLookupChemicalName:
    def test_lookup_chemical_name_returns_expected_value(self, mocker):
        r = mocker.Mock()
        r.status_code = 200
        r.json.return_value = [{"name": "Test Chemical Name"}]
        mocker.patch("optool.requests.get", return_value=r)

        bnf_code = "123456789012345"
        user_agent = "test-user-agent"
        expected_chemical_name = "Test Chemical Name"

        chemical_name = lookup_chemical_name(bnf_code, user_agent)
        assert chemical_name == expected_chemical_name

    def test_lookup_chemical_name_raises_BNFCodeNotFoundError_for_not_found(
        self, mocker
    ):
        r = mocker.Mock()
        r.status_code = 200
        r.json.return_value = []
        mocker.patch("optool.requests.get", return_value=r)

        bnf_code = "123456789012345"
        user_agent = "test-user-agent"

        with pytest.raises(BNFCodeNotFoundError):
            lookup_chemical_name(bnf_code, user_agent)

    def test_lookup_chemical_name_raises_RequestException_for_status_code_gt_400(
        self, mocker
    ):
        r = mocker.Mock()
        r.status_code = 404
        r.raise_for_status.side_effect = HTTPError("404 Not Found")
        mocker.patch("optool.requests.get", return_value=r)

        bnf_code = "123456789012345"
        user_agent = "test-user-agent"

        with pytest.raises(RequestException):
            lookup_chemical_name(bnf_code, user_agent)


class TestFetchICBSpendingData:
    def test_fetch_icb_spending_data_returns_expected_value(self, mocker):
        r = mocker.Mock()
        r.status_code = 200
        r.json.return_value = [
            {"date": "2023-01", "row_name": "ICB A", "items": 100},
            {"date": "2023-01", "row_name": "ICB B", "items": 150},
        ]
        mocker.patch("optool.requests.get", return_value=r)

        bnf_code = "123456789012345"
        user_agent = "test-user-agent"
        expected_spending_data = [
            {"date": "2023-01", "row_name": "ICB A", "items": 100},
            {"date": "2023-01", "row_name": "ICB B", "items": 150},
        ]

        spending_data = fetch_icb_spending_data(bnf_code, user_agent)
        assert spending_data == expected_spending_data

    def test_fetch_icb_spending_data_raises_RequestException_for_status_code_gt_400(
        self, mocker
    ):
        r = mocker.Mock()
        r.status_code = 404
        r.raise_for_status.side_effect = HTTPError("404 Not Found")
        mocker.patch("optool.requests.get", return_value=r)

        bnf_code = "123456789012345"
        user_agent = "test-user-agent"

        with pytest.raises(RequestException):
            fetch_icb_spending_data(bnf_code, user_agent)

    def test_fetch_icb_spending_data_raises_BNFCodeNotFoundError_for_no_data(
        self, mocker
    ):
        r = mocker.Mock()
        r.status_code = 200
        r.json.return_value = []
        mocker.patch("optool.requests.get", return_value=r)

        bnf_code = "123456789012345"
        user_agent = "test-user-agent"

        with pytest.raises(BNFCodeNotFoundError):
            fetch_icb_spending_data(bnf_code, user_agent)


class TestTopMonthlyICBSpending:
    def test_top_monthly_icb_spending_returns_expected_output(self):
        spending_data = [
            {"date": "2023-02", "row_name": "ICB A", "items": 200},
            {"date": "2023-02", "row_name": "ICB B", "items": 50},
            {"date": "2023-01", "row_name": "ICB A", "items": 100},
            {"date": "2023-01", "row_name": "ICB B", "items": 150},
        ]

        expected_output = [
            {"month": "2023-01", "icb": "ICB B"},
            {"month": "2023-02", "icb": "ICB A"},
        ]

        result = top_monthly_icb_spending(spending_data)
        assert result == expected_output


class TestCli:
    def test_optool_outputs_results_if_no_errors(self, mocker):
        # Mock the fetch_org_data and fetch_icb_spending functions to avoid actual API calls
        mocker.patch("optool.get_user_agent", return_value="test-user-agent")
        mocker.patch("optool.lookup_chemical_name", return_value="Clobetasone butyrate")
        mocker.patch(
            "optool.fetch_icb_spending_data",
            return_value=[
                {"date": "2023-01", "row_name": "ICB A", "items": 100},
                {"date": "2023-01", "row_name": "ICB B", "items": 150},
                {"date": "2023-02", "row_name": "ICB A", "items": 200},
                {"date": "2023-02", "row_name": "ICB B", "items": 50},
            ],
        )

        runner = CliRunner()
        result = runner.invoke(main, ["1304000H0AAAAAA"])

        assert result.exit_code == 0
        assert "Clobetasone butyrate" in result.output

        assert "2023-01 ICB B" in result.output
        assert "2023-02 ICB A" in result.output

    def test_optool_exits_with_error_if_user_agent_not_set(self, mocker):
        mocker.patch("optool.get_user_agent", return_value=None)

        runner = CliRunner()
        result = runner.invoke(main, ["1304000H0AAAAAA"])

        assert result.exit_code != 0
        assert (
            "Error: OPENPRESCRIBING_USER_AGENT environment variable is not set."
            in result.output
        )

    def test_optool_exits_with_error_if_invalid_bnf_code(self, mocker):
        mocker.patch("optool.get_user_agent", return_value="test-user-agent")

        runner = CliRunner()
        result = runner.invoke(main, ["12345"])  # Invalid BNF code

        assert result.exit_code != 0
        assert "Error: BNF code must be 15 characters long." in result.output

    def test_optool_exits_with_error_if_lookup_chemical_name_fails(self, mocker):
        mocker.patch("optool.get_user_agent", return_value="test-user-agent")
        mocker.patch(
            "optool.lookup_chemical_name",
            side_effect=BNFCodeNotFoundError(
                "No data found for BNF code 1304000H0AAAAAA"
            ),
        )

        runner = CliRunner()
        result = runner.invoke(main, ["1304000H0AAAAAA"])

        assert result.exit_code != 0
        assert "Error: No data found for BNF code 1304000H0AAAAAA" in result.output
