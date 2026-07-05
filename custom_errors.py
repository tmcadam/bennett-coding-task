"""
This module defines custom exceptions for the OpenPrescribing API tool.
"""


class MissingUserAgentError(Exception):
    """Custom exception raised when the user agent environment variable is not set."""

    pass


class InvalidBNFCodeError(Exception):
    """Custom exception raised when an invalid BNF code is provided."""

    pass


class BNFCodeNotFoundError(Exception):
    """Custom exception raised when a BNF code is not found in the OpenPrescribing API."""

    pass
