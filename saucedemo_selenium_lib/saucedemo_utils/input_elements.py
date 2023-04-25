import time
from abc import abstractmethod
from typing import Tuple

from selenium.common.exceptions import (
    NoSuchElementException,
    ElementClickInterceptedException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from saucedemo_selenium_lib.config import SaucedemoTimeOuts


class BaseInputElement:
    """Made purpose is to update and get html field values"""

    def __init__(self, driver, locator):
        self._driver = driver
        self._locator = locator
        self._parent = None
        self._child = None
        self._element = None

    def set_value(self, value, press_enter=False):
        element = self.find_element()
        element.clear()
        element.send_keys(value)
        if press_enter:
            element.send_keys(value)

    def update_value(self, value, press_enter=False):
        """
        This is for updating fields that produce error when selenium element.clear() is called. It first select the value and replace it with new one.
        """
        element = self.find_element()
        element.send_keys(f"{Keys.CONTROL}a")
        element.send_keys(value)

        if press_enter:
            element.send_keys(Keys.ENTER)

    def set_file_value(self, path):
        element = self.find_element()
        element.send_keys(path)

    def get_value(self):
        element = self.find_element()
        return element.get_attribute("value")

    def click_once_not_obscured_by_loading_screen(self, element):
        try:
            element.click()
        except ElementClickInterceptedException as error:
            if "front_window_highlighter" in error.msg:
                # Obscured by loading screen. Wait and try again
                time.sleep(1)
                self.click_once_not_obscured_by_loading_screen(element)
            else:
                # Obscured by something else.
                raise error

    @abstractmethod
    def find_element(self):
        pass


class InputElementByClass(BaseInputElement):
    def find_element(self):
        try:

            element = WebDriverWait(
                self._driver, SaucedemoTimeOuts.PRODUCT_SHOULD_BE_PRESENT_TIMEOUT
            ).until(EC.presence_of_element_located((By.CLASS_NAME, self._locator)))
            return element

        except NoSuchElementException as e:
            raise


class InputElementById(BaseInputElement):
    def find_element(self):
        try:
            element = WebDriverWait(
                self._driver, SaucedemoTimeOuts.PRODUCT_SHOULD_BE_PRESENT_TIMEOUT
            ).until(EC.element_to_be_clickable((By.ID, self._locator)))
            return element

        except NoSuchElementException as e:
            raise


class InputElementByName(BaseInputElement):
    def find_element(self):
        try:
            element = WebDriverWait(
                self._driver, SaucedemoTimeOuts.PRODUCT_SHOULD_BE_PRESENT_TIMEOUT
            ).until(EC.presence_of_element_located((By.NAME, self._locator)))
            return element

        except NoSuchElementException as e:
            raise


class InputElementByXPath(BaseInputElement):
    def find_element(self):
        try:
            element = WebDriverWait(
                self._driver, SaucedemoTimeOuts.PRODUCT_SHOULD_BE_PRESENT_TIMEOUT
            ).until(EC.presence_of_element_located((By.XPATH, self._locator)))
            return element

        except NoSuchElementException as e:
            raise


class InputElementByLocator(BaseInputElement):
    """
    Pass in locator as tuple or list (locator, name_value)
    """

    def __init__(self, driver, locator: Tuple):
        super().__init__(driver, locator)

    def find_element(self):
        try:
            element = WebDriverWait(
                self._driver, SaucedemoTimeOuts.PRODUCT_SHOULD_BE_PRESENT_TIMEOUT
            ).until(EC.presence_of_element_located(self._locator))
            return element

        except NoSuchElementException as e:
            raise
