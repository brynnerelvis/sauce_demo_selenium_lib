"""
For defining saucedemo test exceptions
"""

from selenium.common.exceptions import NoSuchElementException


class ElementWaitTimeoutException(NoSuchElementException):
    """Custom Exception for wait timeouts when expected elements are not present"""


class SaucedemoTestError(Exception):
    """Base error of the Selenium tests"""

    def __init__(self, message, errors=None):
        super(SaucedemoTestError, self).__init__(message)
        self.errors = errors
        self.message = message


class TargetPathDoesNotExist(SaucedemoTestError):
    """Base error of the selenium  targets"""

    def __init__(self, target_name, target_path, errors=None):
        self.target_name = target_name
        self.target_path = target_path
        message = f"Target :- {target_name} path:- {target_path}-: does not exist"
        super(TargetPathDoesNotExist, self).__init__(message, errors=errors)
