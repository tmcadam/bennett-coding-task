"""
This module defines custom types for the OpenPrescribing API tool.
These types are used to provide type hints for functions and data structures
"""

from typing import TypedDict


class BNFCodeEntry(TypedDict):
    bnf_code: str
    name: str


class OrgDetailEntry(TypedDict):
    date: str
    row_name: str
    total_list_size: int


class SpendingByOrgEntry(TypedDict):
    date: str
    row_name: str
    items: int


class MonthlyICBStats(TypedDict):
    icb: str
    measure: int | float


class MonthlyTopPrescribingICB(TypedDict):
    month: str
    icb: str
