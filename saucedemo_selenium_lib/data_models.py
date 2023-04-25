"""For defining common data structure"""
from enum import Enum


class BaseDataClass:
    @classmethod
    def get_public_attribute_values(cls):
        """Returns list of public attribute values"""
        all_values = []
        for name, value in cls.__dict__.items():
            if not name.startswith("_") and isinstance(value, str):
                all_values.append(value)
        return all_values


class WebBrowsers(Enum):
    """Available WebDrivers that can be used when running tests"""

    CHROME = "chrome"
    FIREFOX = "firefox"

