"""This module is intended to have classes and functions that common to all webapp instances"""

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.select import Select
from saucedemo_selenium_lib.saucedemo_utils import saucedemo_utils as sl
from saucedemo_selenium_lib.saucedemo_utils.input_elements import (
    InputElementByLocator,
    InputElementByXPath,
)
from saucedemo_selenium_lib.locators.common import (
    CommonLocators,
)


class BaseSaucedemoPage:
    """
    Base class for object page that define common functions that can be done on a saucedemo page.
    """

    def __init__(self, saucedemo_utils: sl.SaucedemoUtils, object_name=None):
        self._saucedemo_utils = saucedemo_utils
        self._object_name = object_name

    @property
    def saucedemo_utils(self):
        return self._saucedemo_utils

    def _verify_input_value(self, locator, value):
        """
        Verify given input value is correct
        """
        element = InputElementByLocator(self._saucedemo_utils.driver, locator)
        element_value = element.get_value()
        print(f"Given value: {value}")
        print(f"Actual Input value: {element_value}")
        if element_value == str(value):
            return True
        else:
            return False

    def sort_product_list(self, sort_type: str):
        """Sort the product list using sort type.
        Redundant function. As it has been used a lot in tests. Just call sort_product_list in Saucedemo utils"""
        self.saucedemo_utils.sort_product_list(sort_type)

    def log_in_saucedemo(self):
        """Open saucedemo and login"""
        self._saucedemo_utils.open_saucedemo_website()
        self._saucedemo_utils.login()

    def select_product_by_name(self, product_name):
        """
        Click on a product name to open an object page
        """
        self.saucedemo_utils.is_product_found(product_name)
        self.saucedemo_utils.click_at_a_product_in_products_list(product_name)

    def select_product_by_image(self, product_name):
        """
        Click on a product image to open an object page
        """
        self.saucedemo_utils.is_product_found(product_name)
        self.saucedemo_utils.click_at_a_product_image_in_products_list(product_name)

    def _convert_string_to_slug(self, string: str):
        """
        converts a string to a hyphenated or underscored version
        of the string, depending on whether it contains spaces,
        which could be used to create a slug.

        (A slug is a URL-friendly version of a string that is
        typically used to create a human-readable, search-engine
        -friendly URL for a web page. This is usually created by
        converting a string to lowercase, replacing spaces and
        special characters with hyphens or underscores,and
        removing any other characters that are not alphanumeric
        or underscores.)

        Args:
            string: str

        Returns:
            slug: str

        """
        print(f"string to convert to slug: {string}")
        if ' ' in string:
            # If string has spaces, convert to hyphenated string and lowercase string
            slug = string.lower().replace(' ', '-')
        else:
            # If string has no spaces or with underscores, convert to lowercase string
            slug = string.lower()
        print(f"string {string} converted to slug: {slug}")
        return slug

    def _click_remove_product_button(self, product_name: str):
        product_name_slug = self._convert_string_to_slug(product_name)
        button = InputElementByXPath(
            self._saucedemo_utils.driver,
            f"//button[contains(@id, 'remove-{product_name_slug}') and contains(., 'Remove')]",
        ).find_element()
        button.click()

    def _get_added_products_in_products_page(self):
        try:
            elements = self._saucedemo_utils.get_elements(CommonLocators.ADDED_PRODUCTS)
            products = [product.text for product in elements]
            return products
        except TimeoutException:
            return []

    def remove_product(self, product_name: str):
        """Remove a product from products page"""
        self._click_remove_product_button(product_name)
        product_names = self._get_added_products_in_products_page()
        assert product_name not in product_names

    def verify_text_in_locator(self, locator: tuple, text: str):
        """Verify if the text in the locator exist and it's the same as a given text"""
        try:
            element = self._saucedemo_utils.get_element(locator)
            assert element.text == text
            return True
        except (NoSuchElementException, TimeoutException):
            return False

    def select_option_by_option_text(self, select_locator, option_text):
        """Select selection option by option displayed text"""
        self.saucedemo_utils.logger.info(
            f"Changing selection option locator:- {select_locator}  to: {option_text}"
        )
        select_element = self._saucedemo_utils.get_element(select_locator)
        select = Select(select_element)
        select.select_by_visible_text(option_text)

    def _open_menu(self):
        menu_button = self.saucedemo_utils.get_element(CommonLocators.MENU_BUTTON)
        menu_button.click()

    def close_browser(self):
        """Close web driver. Just provide api to closer browser without having excess to saucedemo_utils"""
        self.saucedemo_utils.close_browser()

