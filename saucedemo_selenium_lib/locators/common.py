"""Locators for common elements/component locators on saucedemo website"""
from selenium.webdriver.common.by import By


class CommonLocators:
    MENU_BUTTON = (By. CLASS_NAME, "bm-burger-button")
    ADDED_PRODUCTS = (By. XPATH, "")
    ERROR_DIALOG = (By.CLASS_NAME, "message-box-error")
    USER_LOGIN_USERNAME = (By. ID, "user-name")
    USER_LOGIN_PASSWORD = (By.ID, "password")
    USER_LOGIN_BTN = (By. ID, "login-button")
    LOGOUT_BUTTON = (By. ID, "logout_sidebar_link")
    SORT_DROP_DOWN = (By. CLASS_NAME, "product_sort_container")
    RESET_APP_STATE = (By. ID, "reset_sidebar_link")
    PRODUCT = (By. CLASS_NAME, "inventory_item")
    PRODUCT_NAMES = (By. CLASS_NAME, "inventory_item_name")
    PRODUCT_PRICES = (By. CLASS_NAME, "inventory_item_price")