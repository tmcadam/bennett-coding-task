"""
This module defines custom types for the OpenPrescribing API tool.
These types are used to provide type hints for functions and data structures
"""

from typing import TypedDict


class SpendingEntry(TypedDict):
    date: str
    row_name: str
    items: int


class MonthlyICBStats(TypedDict):
    icb: str
    measure: int


class MonthlyICBSummary(TypedDict):
    month: str
    icb: str
