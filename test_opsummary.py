from opsummary import (
    top_monthly_prescribing_icbs_by_total_items,
    top_monthly_prescribing_icbs_by_items_per_patient,
)


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
