import os
import yaml

from saucedemo_selenium_lib.data_models import WebBrowsers
from saucedemo_selenium_lib.exceptions import SaucedemoTestError

config_path = os.path.abspath(os.path.join(__file__, "../../../config.yml"))


class TestConfig:
    """For managing Test configs and defining common constants"""

    DATA_PATH = os.path.abspath(os.path.join(__file__, "../../../data/"))
    DOWNLOAD_PATH = os.path.abspath(os.path.join(__file__, "../../../downloads/"))
    OUTPUT_PATH = os.path.abspath(os.path.join(__file__, "../../../output/"))
    SCREENSHOT_PATH = os.path.abspath(os.path.join(__file__, "../../../screenshots/"))
    JS_COVER_REPORT_PATH = os.path.abspath(
        os.path.join(__file__, "../../../jscover/report/")
    )
    JAVASCRIPT_FILE_PATH = os.path.abspath(
        os.path.join(__file__, "../../js/drag_and_drop_helper.js")
    )

    def __init__(
        self,
        host_url=None,
        username=None,
        password=None,
        host_index=None,
        config_file=os.environ.get("CONFIG_PATH", config_path),
        browser=WebBrowsers.CHROME, # this can be updated to any browser such as Firefox, Chrome, etc.
        grid=None,
    ):
        # If host_url , username or  password are set, then respective instance configurations will not be
        # fetched from a config file.
        self._config_file = config_file
        self._host_index = host_index
        self._host_url = host_url
        self._username = username
        self._password = password
        self._browser = browser
        self._grid = grid

    @property
    def host_url(self):
        """Return host url of target test webapp instance"""
        if self._host_url is None:
            self._host_url = self._get_host_url()
        return self._host_url

    @property
    def username(self):
        """Return username of configured users for the webapp instance"""
        if self._username is None:
            self._username = self._get_host_username()
        return self._username

    @property
    def password(self):
        """Return password of configured users for the webapp instance"""
        if self._password is None:
            self._password = self._get_host_password()
        return self._password

    @property
    def config_file_path(self):
        """Config file path"""
        return self._config_file

    @property
    def browser(self):
        return self._browser

    @property
    def grid(self):
        return self._grid

    def _get_configs_dict(self):
        """Get dictionary of configs"""
        try:
            with open(self._config_file) as file:
                configs = yaml.load(file, Loader=yaml.FullLoader)
                return configs
        except FileNotFoundError as e:
            # Config file should be created locally before running the tests
            raise SaucedemoTestError(
                f"config.yml file containing the Webapp Instance configs not found. Please add it in the given path: {self._config_file}.",
                errors=e,
            )

    def _get_host_url(self):
        configs = self._get_configs_dict()
        try:
            return configs["hosts"][self._host_index]["url"]
        except KeyError:
            raise Exception(f"Host url is not available in the configs")

    def _get_host_username(self):
        configs = self._get_configs_dict()
        try:
            return configs["hosts"][self._host_index]["username"]
        except KeyError:
            raise Exception("Host username is not available in the configs")

    def _get_host_password(self):
        configs = self._get_configs_dict()
        try:
            return configs["hosts"][self._host_index]["password"]
        except KeyError:
            raise Exception("Host users password is not available in the configs")


class SaucedemoTimeOuts:
    PRODUCT_SHOULD_BE_PRESENT_TIMEOUT = 10
    LONG_LOADING_TIMEOUT = 30
    SHORT_LOADING_TIMEOUT = 30
