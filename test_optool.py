from requests.exceptions import RequestException
from click.testing import CliRunner

from custom_errors import BNFCodeNotFoundError
from optool import (
    top_monthly_prescribing_icbs_by_total_items,
    top_monthly_prescribing_icbs_by_items_per_patient,
    main,
    get_user_agent,
    valid_bnf_code,
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


class TestTopMonthlyPrescribingICBs:
    def test_top_monthly_prescribing_icbs_returns_expected_output(self):
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

        result = top_monthly_prescribing_icbs_by_total_items(spending_data)
        assert result == expected_output

    def test_top_monthly_icb_spending_with_patient_count_data(self):
        spending_data = [
            {"date": "2023-02", "row_name": "ICB A", "items": 200},
            {"date": "2023-02", "row_name": "ICB B", "items": 50},
            {"date": "2023-01", "row_name": "ICB A", "items": 100},
            {"date": "2023-01", "row_name": "ICB B", "items": 150},
        ]

        patient_count_data = [
            {"date": "2023-02", "row_name": "ICB A", "total_list_size": 1000},
            {"date": "2023-02", "row_name": "ICB B", "total_list_size": 500},
            {"date": "2023-01", "row_name": "ICB A", "total_list_size": 800},
            {"date": "2023-01", "row_name": "ICB B", "total_list_size": 600},
        ]

        expected_output = [
            {"month": "2023-01", "icb": "ICB B"},
            {"month": "2023-02", "icb": "ICB A"},
        ]

        result = top_monthly_prescribing_icbs_by_items_per_patient(
            spending_data, patient_count_data
        )
        assert result == expected_output


class TestCli:
    def test_optool_outputs_results_if_no_errors(self, mocker):
        # Mock the fetch_org_data and fetch_icb_spending functions to avoid actual API calls
        mocker.patch("optool.get_user_agent", return_value="test-user-agent")
        mocker.patch(
            "optool.OpenPrescribingClient.fetch_chemical_name",
            return_value="Clobetasone butyrate",
        )
        mocker.patch(
            "optool.OpenPrescribingClient.fetch_icb_spending_data",
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
            "optool.OpenPrescribingClient.fetch_chemical_name",
            side_effect=BNFCodeNotFoundError(
                "No data found for BNF code 1304000H0AAAAAA"
            ),
        )

        runner = CliRunner()
        result = runner.invoke(main, ["1304000H0AAAAAA"])

        assert result.exit_code != 0
        assert "Error: No data found for BNF code 1304000H0AAAAAA" in result.output

    def test_optool_exits_with_error_if_fetch_icb_spending_data_fails(self, mocker):
        mocker.patch("optool.get_user_agent", return_value="test-user-agent")
        mocker.patch(
            "optool.OpenPrescribingClient.fetch_chemical_name",
            return_value="Clobetasone butyrate",
        )
        mocker.patch(
            "optool.OpenPrescribingClient.fetch_icb_spending_data",
            side_effect=RequestException(
                "Failed to fetch data from OpenPrescribing API"
            ),
        )

        runner = CliRunner()
        result = runner.invoke(main, ["1304000H0AAAAAA"])

        assert result.exit_code != 0
        assert "Error: Failed to fetch data from OpenPrescribing API" in result.output
