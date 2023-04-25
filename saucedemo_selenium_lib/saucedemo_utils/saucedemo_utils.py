import time, os
import logging

from datetime import datetime
from string import Template
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.command import Command
from selenium.webdriver.support.events import EventFiringWebDriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    NoSuchElementException,
    TimeoutException,
    JavascriptException,
)
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from saucedemo_selenium_lib.config import SaucedemoTimeOuts, TestConfig
from saucedemo_selenium_lib.data_models import WebBrowsers
from saucedemo_selenium_lib.event_listeners import SeleniumEventListener
from saucedemo_selenium_lib.saucedemo_utils.input_elements import InputElementByLocator
from saucedemo_selenium_lib.locators.common import CommonLocators
from saucedemo_selenium_lib.exceptions import (
    SaucedemoTestError,
    ElementWaitTimeoutException,
)
from saucedemo_selenium_lib.helpers import (
    get_current_running_test_full_name,
    create_folder_if_non_exist,
)


class SaucedemoUtils:
    """SaucedemoUtils

    Class containing common operations on Saucedemo webapp. This the core class for Selenium tests.

    Attributes:
        saucedemo_url: URL of target Saucedemo webapp where the tests will be run
        username: Login username for Target Saucedemo webapp
        password: Password of login user for target Saucedemo webapp
        headless: Flag if true run tests in headless mode. i.e browser is not opened while running tests

    """

    def __init__(
        self,
        saucedemo_url,
        username="",
        password="",
        headless=True,
        output_path=TestConfig.OUTPUT_PATH,
        download_path=TestConfig.DOWNLOAD_PATH,
        jscover_folder_name=None,
        log_file=None,
        proxy_server=None,
        monitoring_test=False,
        webdriver_cache_valid_range=30,
        browser: WebBrowsers = WebBrowsers.CHROME,
        grid=None,
    ):
        """initialises SaucedemoUtils

        Args:
            saucedemo_url: URL of target Saucedemo webapp where the tests will be run
            username: Login username for Target Saucedemo webapp
            password: Password of login user for target Saucedemo webapp
            headless: Flag if true run tests in headless mode. i.e browser is not opened while running tests. Defaulted to True
            output_path: Path where any created outputs like log files etc , would be saved
            download_path: Path downloads  would be  saved to
            jscover_folder_name: Folder where JS code coverage will be saved to. Only used when monitoring_test is True
            log_file: File name to log to.
            proxy_server: Proxy Server where selenium tests will be run if any
            monitoring_test: Flag if set to True turn on the monitoring JS code coverage while running tests.
                             Monitoring is not completely implemented.
            browser: Enum value  of WebBrowsers. Specify which browser tests will be run in. Defaulted to WebBrowsers.
            grid: url of the grid to run the test, if it isn't defined the test will run locally .Default None

        TODO:
            * JS code coverage implementation is not complete

        """

        create_folder_if_non_exist(output_path)
        create_folder_if_non_exist(download_path)
        self.saucedemo_url = saucedemo_url
        self._browser = browser
        self._webdriver_cache_valid_range = webdriver_cache_valid_range
        self.username = username
        self.password = password
        self.headless = headless
        self.monitoring_test = monitoring_test
        self._proxy_server = proxy_server
        self._output_path = output_path
        self._download_path = download_path
        self._driver = None
        self._event_firing_driver = None  # for listening to and firing events
        self._log_file = self._get_log_file_name(log_file)
        self._logger = self._initialise_logger()
        self._jscover_name = jscover_folder_name
        self._grid = grid
        self._common_locators = CommonLocators()
        self.logger.info(f"Running tests on Saucedemo webapp:- {self.saucedemo_url}")

    def __del__(self):
        """
        Check and close browser if it is not closed.
        __del__ will always run when all references to SaucedemoUtils webapp instance have been eliminated.
        Used to clean up after a test. Sometimes test writers may forget to
        close browser. We need to clean it up during object destruction since when this function is called all references
        to it have been destroyed.
        This is a workaround fix in case close_browser() is not called in the test's teardown.
        It MUST be always ensured that self.close_browser() is explicitly called in the teardown function after each test finished.

        Warning: DON'T call self.close_browser() in another class __del__ where SaucedemoUtils is used. That would cause
        ImportError: sys.meta_path is None, Python is likely shutting down. This is likely caused because of the order the selenium driver is executing self.driver.quit()
        """

        if not self.is_web_driver_quited:
            self.close_browser()

    @property
    def driver(self):
        """Current instance of Selenium Web Driver"""
        return self._driver

    @property
    def event_firing_driver(self):
        """Webdriver which listens for and fires events for event-driven control flow"""
        return self._event_firing_driver

    @driver.setter
    def driver(self, driver):
        """Set webdriver to a new instance provided driver"""
        self._driver = driver

    @property
    def common_locators(self):
        """Return Instance of CommonLocators"""
        return self._common_locators

    @property
    def logger(self):
        """Return instance of Logger"""
        return self._logger

    @property
    def is_web_driver_quited(self):
        """Check if driver.quit()
        Send driver Command.STATUS execute command.

        Examples:
            when calling self._driver.execute(Command.STATUS) and driver is driver.quit is not called , it return
            {'value': {'build': {'version': '91.0.4472.19 (1bf021f248676a0b2ab3ee0561d83a59e424c23e-refs/branch-heads/4
            472@{#288})'},
            'message': 'ChromeDriver ready for new sessions.', 'os': {'arch': 'x86_64', 'name': 'Linux',
            'version': '5.8.0-59-generic'}, 'ready': True}}
            However, it raises an error if it has already been called

        Return true if there is given  exceptions(socket.error, CannotSendRequest, MaxRetryError, NewConnectionError) when calling self._driver.execute(Command.STATUS)
        """
        if self._driver:
            try:
                self._driver.execute(Command.STATUS)
                self.logger.info("Web browser is not closed")
                return False

            except Exception as e:
                self.logger.info("Web browser is already closed.")
                self.logger.info(f"Exception:- {e}")

                return True
        else:
            # when driver is None. e.g never created
            return True

    def login(self, username=None, password=None, wait=True, timeout=180):
        """Login to Saucedemo webapp with credentials

        By default, username and password provided in the instantiation will be used unless they are set as args here

        Args:
            username: User username to be logged.
            password: Password of the login user
            wait: Flag is set then wait for MENU_BUTTON element to be present on Saucedemo webapp. Defaulted to True
            timeout: Timeout when waiting for elements to be available on Sucedemo. Default is 180 seconds

        Returns: None

        """
        if username is None:
            username = self.username
        if password is None:
            password = self.password

        self.save_field_value(
            self.common_locators.USER_LOGIN_USERNAME, username, click_after=False
        )
        self.save_field_value(
            self.common_locators.USER_LOGIN_PASSWORD, password, click_after=False
        )
        self.click_at_element(self.common_locators.USER_LOGIN_BTN)

        if wait:
            self.wait_for_element(
                self.common_locators.MENU_BUTTON,
                timeout=timeout,
            )

    def logout(self):
        """Logout current logged user"""
        action = ActionChains(self.driver)
        user_menu_button = self.get_element(CommonLocators.MENU_BUTTON)
        user_menu_button.click()

        action.move_to_element(
            WebDriverWait(self.driver, 2).until(
                EC.presence_of_element_located(CommonLocators.LOGOUT_BUTTON)
            )
        ).click()
        action.perform()
        # Assert logout worked
        login_screen = WebDriverWait(
            self.driver, SaucedemoTimeOuts.SHORT_LOADING_TIMEOUT
        ).until(EC.element_to_be_clickable((CommonLocators.USER_LOGIN_BTN)))
        assert login_screen is not None

    def close_browser(self):
        """Call this function at the end of each teach save jscover and/ close opened driver browsers"""
        self.logger.info("Closing browser")
        if self._proxy_server:
            self._save_js_cover_report()

        if not self.is_web_driver_quited:
            self._event_firing_driver.quit()

    def _save_js_cover_report(self):
        """Save JSCover report from local storage into files"""
        self.logger.info("Saving JSCover Coverage Data in browser")
        if self._jscover_name is None:
            raise ValueError(
                f"JS Cover folder name(jscover_name ) must not be none when saving JSCover Report"
            )
        save_report_action_template = "jscoverage_report('$folder_name', function(){window.jscoverFinished=true;});"
        save_report_command = Template(template=save_report_action_template).substitute(
            folder_name=self._jscover_name
        )

        try:
            self.driver.execute_script(save_report_command)
            self.driver.execute_script("return window.jscoverFinished;")
        except JavascriptException:
            raise SaucedemoTestError(
                f"Saucedemo is not instrumented by JSCover Proxy server. Please check that proxy server:- {self._proxy_server} -: is started"
            )

    def _get_log_file_name(self, log_file):
        if log_file:
            return log_file

    def _initialise_logger(self):
        if self.monitoring_test:
            log_level = logging.ERROR
        else:
            log_level = logging.INFO

        logging.basicConfig(
            filename=os.path.join(self._output_path, f"{self._log_file}.log"),
            filemode="w",
            format="%(asctime)s - %(message)s",
            level=log_level,
        )
        logger = logging.getLogger(__name__)
        if not logger.handlers:
            logger.addHandler(logging.StreamHandler())
        return logger

    def _setup_web_driver(self):
        """
        Sets up the web driver for either firefox or chrome.
        """
        self._driver = None
        if self._browser == WebBrowsers.FIREFOX:
            self._driver = self._create_firefox_driver()
        else:
            self._driver = self._create_chrome_driver()

        self.driver.maximize_window()

        self._event_firing_driver = EventFiringWebDriver(
            self._driver, SeleniumEventListener(self)
        )

    def setup_chrome_driver_mode(self, headless=True):
        """Set the headless mode after SaucedemoUtils is instantiated

        Only use to change headless mode to True or False.

        Args:
            headless: True or False bool value to set headless mode

        """
        self.headless = headless

    def _get_remote_webdriver(self, options):
        """Setup the remote webdriver based on the browser and grid url given by parameters"""
        desired_capabilities = {
            "browserName": self._browser.value,
            "acceptInsecureCerts": True,
            "networkConnectionEnabled": True
        }
        return webdriver.Remote(
            command_executor=self._grid,
            options=options,
            desired_capabilities=desired_capabilities
        )

    def _create_chrome_driver(self):
        """Setup chrome driver. Call automatically right when website is being opened"""
        self.logger.info("Setting up Chrome Driver")
        chrome_options = self._get_web_driver_options()
        prefs = {"download.default_directory": self._download_path}
        chrome_options.add_experimental_option("prefs", prefs)
        if self._proxy_server:
            proxy = self._get_chrome_proxy()
            return webdriver.Chrome(
                executable_path=ChromeDriverManager(
                    cache_valid_range=self._webdriver_cache_valid_range
                ).install(),
                options=chrome_options,
                desired_capabilities=proxy,
            )
        else:
            if self._grid is None:
                return webdriver.Chrome(
                    executable_path=ChromeDriverManager(
                        cache_valid_range=self._webdriver_cache_valid_range
                    ).install(),
                    options=chrome_options,
                )
            else:
                return self._get_remote_webdriver(options=chrome_options)

    def _get_chrome_proxy(self):
        """
        Get and returns capabilities of chrome proxy.
        """
        proxy = Proxy()
        proxy.proxy_type = ProxyType.MANUAL
        proxy.http_proxy = self._proxy_server
        capabilities = webdriver.DesiredCapabilities.CHROME
        proxy.add_to_capabilities(capabilities)
        return capabilities

    def _get_web_driver_options(self):
        """
        Get webdriver options either Firefox or Chrome, add
        arguements in options, and return the options.
        """
        if self._browser == WebBrowsers.FIREFOX:
            options = FirefoxOptions()
        else:
            options = ChromeOptions()
        if self.headless:
            options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-gpu")
        options.add_argument("--enable-logging")
        options.add_argument("--log-level=0")
        options.add_argument("--ignore-certificate-errors")
        return options

    def _create_firefox_driver(self):
        """Create Firefox selenium webdriver"""
        self.logger.info("Setting up Firefox Driver")
        self.logger.info("Setting up FIREFOX Profile")
        options = self._get_web_driver_options()
        options.set_preference("browser.download.folderList", 2)
        options.set_preference("browser.download.manager.showWhenStarting", False)
        options.set_preference("browser.download.dir", self._download_path)
        options.set_preference(
            "browser.helperApps.neverAsk.saveToDisk",
            "text/html, application/octet-stream, text/plain, "
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        if self._grid is None:
            return webdriver.Firefox(
                executable_path=GeckoDriverManager(
                    cache_valid_range=self._webdriver_cache_valid_range
                ).install(),
                options=options,
            )
        else:
            return self._get_remote_webdriver(options=options)

    def is_element_available(self, locator, timeout=3, print_logs=True):
        """Check is an object of a given locator is available on the page"""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            if print_logs:
                self.logger.info(f"Element Found: {locator}")
            return True
        except (TimeoutException, NoSuchElementException):
            if print_logs:
                self.logger.info(f"Element not Found: {locator}")
            return False

    def wait_until_element_is_available(
        self, locator, sleep_time=2, timeout=SaucedemoTimeOuts.LONG_LOADING_TIMEOUT,
    ):
        """
        Wait until an element of a given locator is available. breakout of loop if timeout is reached

        Args:
            locator: Tuple containing locator of the HTML element
            sleep_time: Time to sleep whenever element checked if not available. Default value is 2 seconds
            timeout: Timeout to wait element is available. If timeout is reached, a warning message will be printed out
                     and the function return(While loop is exited)

        """
        total_time = 0
        self._logger.info(f"Checking for presence of element with locator :{locator}")
        while self.is_element_available(locator, timeout=1) is False:
            time.sleep(sleep_time)
            total_time += sleep_time
            self._logger.info(
                f"Waiting until element with locator :{locator}---- Total wait time: {total_time} seconds"
            )
            if total_time > timeout:
                self._logger.warning(
                    f"Can not find element with locator: {locator} for : {timeout} seconds"
                )
                break

    def open_saucedemo_website(self):
        """
        Open Saucedemo website and expect login page

        Returns: None

        """
        self._setup_web_driver()
        print(self._browser)
        self.driver.get(self.saucedemo_url)
        WebDriverWait(self.driver, SaucedemoTimeOuts.LONG_LOADING_TIMEOUT).until(
            EC.element_to_be_clickable((By.NAME, "username"))
        )
        self.wait_until_element_is_available(self.common_locators.USER_LOGIN_USERNAME)

    def is_product_found(self, product_name: str):
        """Check if product in the products list is of the  given product name

        Args:
            product_name: str

        Returns:
            boolean

        """
        product_name_locator = (
            By.XPATH,
            f"//div[contains(@class, 'inventory_item_name') "
            f"and contains(., '{product_name}')]"
        )
        self.logger.info(f"Checking product availability: {product_name}")
        return self.is_element_available(product_name_locator)

    def click_at_a_product_in_products_list(
            self,
            product_name,
            track_warning_errors=True,
    ):
        """Click on product name in products list page"""
        product_name_locator = (
            By.XPATH,
            f"//div[contains(@class, 'inventory_item_name') "
            f"and contains(., '{product_name}')]"
        )
        self.click_at_element(
            element_locator=product_name_locator,
            track_warning_errors=track_warning_errors,
        )

    def click_at_a_product_image_in_products_list(
            self,
            product_name,
            track_warning_errors=True,
    ):
        """Click on product image in products list page"""
        product_image_locator = (
            By.XPATH,
            f"//img[contains(@class, 'inventory_item_img') "
            f"and contains(@alt, '{product_name}')]"
        )
        self.click_at_element(
            element_locator=product_image_locator,
            track_warning_errors=track_warning_errors,
        )

    def click_at_element(self, element_locator, track_warning_errors=True):
        """Click at an element of given element_locator

        Args:
            element_locator: Selenium locator of an element to be clicked
            track_warning_errors: Set to True if you want to check for errors
            after the update. Default is True

        Returns: None

        Raises:
            ElementClickInterceptedException if element click is intercepted
            by another element. A Click can be intercepted
            by another element that might obscure the target

        """

        self.wait_until_element_is_available(element_locator)
        btn = self.wait_for_element(element_locator)
        btn.location_once_scrolled_into_view
        try:
            btn.click()
        except ElementClickInterceptedException:
            self.driver.execute_script("arguments[0].click();", btn)
        if track_warning_errors:
            self._take_screenshot_on_warning_errors()

    def wait_for_element(
        self,
        by_tuple,
        timeout=SaucedemoTimeOuts.LONG_LOADING_TIMEOUT,
        wait_for_clickable=True,
    ):
        """Wait for an element to be clickable and return it

        Args:
            timeout (int): Maximum time to wait for the element
            by_tuple (tuple(Locator, str)): The element to wait for as
                selenium.webdriver.common.by.By
            wait_for_clickable: Wait until the element is clickable if set
            to True otherwise it just waits until element is available

        Returns:
            WebComponent: The element to wait for
        """
        try:
            if wait_for_clickable:
                return WebDriverWait(self.driver, timeout).until(
                    EC.element_to_be_clickable(by_tuple)
                )
            else:
                return WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located(by_tuple)
                )
        except NoSuchElementException:
            msg = f"Timed out waiting for element {by_tuple[1]}"
            raise ElementWaitTimeoutException(msg)

    def _take_screenshot_on_warning_errors(self):
        """Take screenshot when error box is available"""
        if self.is_element_available(
            self.common_locators.ERROR_DIALOG
        ) or self.is_element_available(self.common_locators.ERROR_DIALOG):
            self.logger.info("There is an error dialog box after test")
            file_name = get_current_running_test_full_name()
            file_path = os.path.join("errors-warnings", file_name)
            self.take_screenshot(file_name=file_path)

    def take_screenshot(
        self,
        screenshot_path=TestConfig.SCREENSHOT_PATH,
        file_name="screenshot",
    ):
        """Take a screenshot of current open page

        Args:
            screenshot_path: Path where screenshot is saved. Default is
            TestConfig.SCREENSHOT_PATH
            file_name: Name of the screenshot file. Default is 'screenshot'

        Returns:
            screenshot full file path

        """
        date_time = datetime.now()
        file_name = f"{file_name}-{date_time}.png"
        file_path = os.path.join(screenshot_path, file_name)
        self.driver.save_screenshot(file_path)
        return file_path


    def get_element(self, locator, timeout=SaucedemoTimeOuts.SHORT_LOADING_TIMEOUT):
        """Get any html element of a given Selenium locator

        Args:
            locator: Locator tuple of the element to be retrieved
            timeout: Timeout to wait until the element is available. Default is HiveTimeOuts.OBJ_SHOULD_BE_PRESENT_TIMEOUT

        Returns:
            element with the given locator

        Raises:
            TimeoutException if element is not found until the timeout is not reached

        """
        self.logger.info(f"Getting element with locator :{locator}")
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            return element
        except TimeoutException as e:
            raise

    def get_elements(self, locator, timeout=SaucedemoTimeOuts.SHORT_LOADING_TIMEOUT):
        """Return list of elements with given Selenium locator

        Args:
            locator: Locator of the elements expected
            timeout: Timeout to wait until the element is available. Default is HiveTimeOuts.OBJ_SHOULD_BE_PRESENT_TIMEOUT

        Returns:
            list of elements

        Raises:
            TimeoutException if no element matching the locator is not found until the timeout is not reached

        """
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_all_elements_located(locator)
            )
            return element

        except TimeoutException as e:
            raise

    def get_child_elements(self, parent_element, child_locator):
        """Return list of elements with given Selenium locator inside parent element

        Args:
            parent_element: Selenium locator of the parent element
            child_locator: selenium locator of the child element

        Returns:
            child element matching the child_locator

        Raises:
            NoSuchElementException if child element is not found

        """
        try:
            children = parent_element.find_elements(child_locator[0], child_locator[1])
            return children
        except NoSuchElementException:
            raise

    def get_child_element(self, parent_element, child_locator):
        """Get child element inside another element

        Args:
            parent_element: Selenium locator of the parent element
            child_locator: Selenium locator of the child element

        Returns:
            child element

        Raises:
            NoSuchElementException if child element is not found

        """
        try:
            children = parent_element.find_element(child_locator[0], child_locator[1])
            return children
        except NoSuchElementException:
            raise

    def select_input_by_visible_text(self, locator, text):
        """Select option for HTML select input by text.

        Args:
            locator: Locator of the HTML Select input field
            text: Text of the option to be selected

        Returns: None

        """
        options = Select(self.get_element(locator))
        options.select_by_visible_text(text)

    def save_field_value(
        self,
        locator,
        value,
        press_enter=False,
        click_after=True,
        track_warning_errors=True,
    ):
        """Update value of html field element

        Args:
            locator: Selenium locator of the html field element
            value: New value of html field element
            press_enter: Set this flag to True to send ENTER command to the field after update the value. Default is False
            click_after: Set this flag to True to click somewhere on the page after updating the value. Default is True
                         Clicking on Saucedemo page trigger Saucedemo Frontend to send update requests to the Backend
            track_warning_errors: Set to True if you want to check for errors after the update. Default is True

        Returns: None

        """
        element = InputElementByLocator(self.driver, locator)
        element.update_value(value, press_enter)
        if click_after:
            self.click_somewhere_on_page()  # trigger  a request to save the value
        if track_warning_errors:
            self._take_screenshot_on_warning_errors()

    def click_somewhere_on_page(self, locator=(By.ID, "root")):
        """Click somewhere on page

        Args:
            locator: locator of the element on the Sacuedemo webapp to click at. Click at root div by default

        Returns:
            None

        """
        element = self.get_element(locator)
        element.click()

    def verify_input_value(self, locator, value):
        """Verify given input value is correct

        Args:
            locator: Selenium locator of the input field where the value is expected
            value: Value to verify

        Returns:
            True if the given value is the input field value. False otherwise

        """

        element = InputElementByLocator(self.driver, locator)
        if element.get_value() == value:
            return True
        else:
            return False

    def sort_product_list(self, sort_type: str):
        """
        Sorts the product list based on product type.

        Args:
            sort_type: str

        Return:
            None

        """
        self.select_input_by_visible_text(
            locator=self.common_locators.SORT_DROP_DOWN,
            text=sort_type,
        )