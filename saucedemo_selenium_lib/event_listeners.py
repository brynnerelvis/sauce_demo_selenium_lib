import os.path

from selenium.webdriver.support.events import AbstractEventListener
from saucedemo_selenium_lib.helpers import get_current_running_test_full_name


class SeleniumEventListener(AbstractEventListener):
    def __init__(self, saucedemo_utils):
        self.saucedemo_utils = saucedemo_utils

    def before_quit(self, driver):
        """Fired just before the browser is being closed. Check for dialog boxes after the tests is finished
        and take screenshot if the warning or errors are found"""
        self.saucedemo_utils.logger.info(
            "Checking for presence of warning and error dialog boxes"
        )
        if self.saucedemo_utils.is_element_available(
            self.saucedemo_utils.common_locators.ERROR_DIALOG
        ):
            self.saucedemo_utils.logger.info(
                "There was an error dialog box displayed after the test concluded."
            )
            try:
                file_name = get_current_running_test_full_name()
                file_path = os.path.join("errors-warnings", file_name)
                self.saucedemo_utils.take_screenshot(file_name=file_path)
            except (ValueError, FileNotFoundError) as e:
                # Any exception here should not affect a test results. This check is for logging purposes only
                self.saucedemo_utils.logger.warning(
                    f"Exception while checking for dialog boxes before quiting browser: {e}"
                )
