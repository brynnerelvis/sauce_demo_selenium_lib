"""For selenium tests decorators"""
import inspect
import os
from functools import partialmethod
from saucedemo_selenium_lib.config import TestConfig
from datetime import datetime
import unittest

from saucedemo_selenium_lib.helpers import create_folder_if_non_exist


def screenshot_on_fail(
    saucedemo_utils_attr="saucedemo_utils",
    screenshot_path=TestConfig.SCREENSHOT_PATH,
    hexagon_folder="",
):
    def wrapper(cls):
        def with_screen_shot(self, fn, *args, **kwargs):
            """Take a Screen-shot of the selenium driver page, when a test fails."""
            class_name = f"{cls.__name__}"

            print(f"Decorating class: {class_name}")
            try:

                return fn(self, *args, **kwargs)
            except unittest.SkipTest:
                print("Skipped Test")

            except Exception:
                # Any exception raised when a test fail
                create_folder_if_non_exist(screenshot_path)
                hive_utils = getattr(self, saucedemo_utils_attr)
                class_function_name = f"{cls.__name__}-{fn.__name__}"
                date_time = datetime.now()
                filename = f"{class_function_name}-{date_time}.png"
                folder_path = os.path.join(screenshot_path, hexagon_folder)
                create_folder_if_non_exist(folder_path)

                file_path = os.path.join(screenshot_path, hexagon_folder, filename)
                hive_utils.driver.get_screenshot_as_file(file_path)
                print(f"Screenshot saved: {file_path}")
                raise

        for name, func in inspect.getmembers(
            cls,
            lambda x: inspect.isfunction(x) or inspect.ismethod(x),
        ):

            if name[:5] == "test_":
                if not is_test_skipped(func):
                    setattr(cls, name, partialmethod(with_screen_shot, func))
                elif name == "setUp":
                    setattr(cls, name, partialmethod(with_screen_shot, func))
                if name == "setUpClass":
                    setattr(
                        cls,
                        name,
                        partialmethod(with_screen_shot, func, cls_or_self=cls),
                    )

        return cls

    return wrapper


def is_test_skipped(func):
    """Inspect the test function and check if test has skipped decorator e.g unittest.skip, pytest.mark.skip"""
    decorators = get_decorators(func)
    for decorator in decorators:
        print(decorator)
        if "unittest.skip" in decorator or "pytest.mark.skip" in decorator:
            print(f"Skipped")
            return True
    return False


def get_decorators(func):
    """Inspect the test function and get list of decorators"""
    source_code = inspect.getsource(func)
    source_code_list = source_code.split()

    stop_index = source_code_list.index("def")
    decorators = source_code_list[:stop_index]
    return decorators
