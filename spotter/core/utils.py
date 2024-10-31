import re
from typing import TypedDict, TypeVar

from spotter.core.exceptions import ApplicationError


class _WGS84(TypedDict):
    latitude: float
    longitude: float


# Custom type constrained to WGS84 format
WGS84Type = TypeVar("WGS84Type", bound=_WGS84)


class ValidateWGS84Value:
    @staticmethod
    def is_valid_wgs84(coordinate_string, raise_error=True):
        """
        Validates a WGS84 coordinate string.

        :param coordinate_string: The string to validate, in the format "latitude,longitude".
        :param raise_error: Whether to return validation boolean value or raise an Application exception
        :return:
            if raise_error=False: True if the string is a valid WGS84 coordinate, False otherwise.
            else if raise_error=True: throws an ApplicationException
        """

        pattern = (
            r"^([-+]?(?:90(?:\.0+)?|[1-8]?\d(?:\.\d+)?)),"
            r"\s*([-+]?(?:180(?:\.0+)?|(?:1[0-7]\d|\d{1,2})(?:\.\d+)?))$"
        )
        flag = bool(re.match(pattern, coordinate_string))
        if raise_error and not flag:
            raise ApplicationError(
                f"Value {coordinate_string} is not a valid WGS84 value (e.g. 38.889805, -77.009056)"
            )
        return flag
