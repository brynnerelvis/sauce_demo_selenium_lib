""" Tests Runner

Contain classes or functions for Tests runner. These include SaucedemoTestRunner for running tests locally
and SaucedemoWebAppTestRunner for running tests remotely on a server like a web testing cockpit, pipelines etc
"""

import os

import pytest
from typing import List

from saucedemo_selenium_lib.exceptions import TargetPathDoesNotExist
from saucedemo_selenium_lib.config import TestConfig

from saucedemo_selenium_lib.test_result.results import HTMLTestResultsParser, ResultsTableCreator

class BaseTestRunner:
    def __init__(self, tests_path: str, output_path=TestConfig.OUTPUT_PATH, headless=1, browser="chrome", grid=None):
        self._tests_path = tests_path
        self._output_path = output_path
        self._headless = headless
        self._py_tests_arguments = []
        self._browser = browser
        self._grid = grid

    @property
    def tests_path(self):
        return self._tests_path

    @property
    def browser(self):
        return self._browser

    @property
    def headless(self):
        return self._headless

    @property
    def py_tests_arguments(self):
        return self._py_tests_arguments

    @property
    def grid(self):
        return self._grid

    def _get_copy_of_py_tests_arguments(self):
        """Return a copy of py_tests_arguments

        Returns:
            py_tests_arguments(list): Copy of Instance py_tests_arguments
        """

        # copy this to avoid persisting changes in self._py_tests_arguments.copy() if you just assign it
        py_tests_arguments = self._py_tests_arguments.copy()
        return py_tests_arguments


class SaucedemoTestRunner(BaseTestRunner):
    """For running tests. It run tests in parallel using"""

    def __init__(
        self,
        tests_path: str,
        tests_to_run: List,
        load_scope_targets=None,
        num_processes=2,
        host_index=None,
        headless=1,
        output_path=TestConfig.OUTPUT_PATH,
        browser="chrome",
        grid=None,
    ):
        """ "
        Run Given tests.

        """
        super().__init__(tests_path, output_path, headless, browser=browser, grid=grid)

        self._load_scope_targets = load_scope_targets
        self._load_scope_targets.extend(load_scope_targets)

        self._targets = self.get_targets_to_test(tests_to_run)
        self._num_processes = num_processes
        self._host_index = host_index

        self._results = []
        self._py_tests_arguments = [
            "--runner",
            "manual",
            "--browser",
            self.browser,
            "-s",
            "-v",
            "--capture",
            "no",
            "--host_index",
            f"{self._host_index}",
            "--headless",
            f"{self._headless}",
            "-n",
            f"{self._num_processes}",
        ]
        if self.grid is not None:
            self._py_tests_arguments.extend(
                ["--grid", f"{self.grid}"]
            )

    @property
    def targets(self):
        return self._targets

    @property
    def output_path(self):
        return self._output_path

    @property
    def results(self):
        return self._results

    @property
    def load_scope_targets(self):
        return self._load_scope_targets

    @property
    def num_processes(self):
        return self._num_processes

    @property
    def host_index(self):
        return self._host_index

    def get_targets_to_test(self, given_targets):
        if len(given_targets) > 0:
            print(f"Targets specified: {given_targets}")

            return self._get_given_targets(given_targets)
        else:
            return self._get_all_targets()

    def _get_all_targets(self):
        """Get all targets in test folder if no targets are specified. This is a feature to run all targets"""
        return [
            _target
            for _target in os.listdir(self._tests_path)
            if "__" not in _target
        ]

    def _get_given_targets(self, targets):
        _targets = []
        for _target in targets:
            path = os.path.join(self._tests_path, _target)
            if os.path.exists(path):
                _targets.append(_target)
            else:
                raise TargetPathDoesNotExist(target_name=_target, target_path=path)
        return _targets

    def run(self):
        """Run given tests"""
        for target in self._targets:
            print(f"Testing: {target}")
            self._run(target)

        print("All target done")
        result_table_creator = ResultsTableCreator(self._results, self._output_path)
        result_table_creator.create_results_table()

    def _run(self, target):
        print(f"Current Target being tested: {target}")
        path = os.path.join(self._tests_path, target)
        xml_report = os.path.join(self._output_path, f"{target}-report.xml")
        html_report = os.path.join(self._output_path, f"{target}-report.html")
        py_tests_arguments = self._get_copy_of_py_tests_arguments()
        py_tests_arguments.extend(["--junitxml", xml_report])
        py_tests_arguments.extend(["--html", html_report])
        if target in self.load_scope_targets or self._num_processes == 1:
            py_tests_arguments.extend(["--dist", "loadscope"])

        py_tests_arguments.append(path)
        print(f"arguments: {py_tests_arguments}")
        pytest.main(args=py_tests_arguments)

        print(f"Tests for Target: {target} started")
        print("Waiting")

        html_parser = HTMLTestResultsParser(target_name=target, file_path=html_report)
        self._results.append(html_parser.get_tests_results())

        print(f"Tests for Target: {target} finished")


class SaucedemoPipelineTestRunner(SaucedemoTestRunner):
    """For running tests. It run tests in parallel using"""

    def __init__(
        self,
        tests_path: str,
        tests_to_run: List,
        host_url: str,
        username: str,
        password: str,
        load_scope_targets=None,
        num_processes=2,
        headless=1,
        output_path="",
        browser="chrome",
        grid=None,
    ):
        """ "
        Run Given tests.

        """
        super().__init__(tests_path, tests_to_run, load_scope_targets, output_path, num_processes, headless=headless, browser=browser, grid=grid)
        self._username = username
        self._password = password
        self._host_url = host_url

        self._py_tests_arguments = [
            "--runner",
            "app",
            "--browser",
            self.browser,
            "--url",
            self._host_url,
            "--username",
            self._username,
            "--password",
            self._password,
            "-v",
            "--capture",
            "sys",
            "--headless",
            f"{self._headless}",
        ]
        if self.grid is not None:
            self._py_tests_arguments.extend(
                ["--grid", f"{self.grid}"]
            )

    @property
    def username(self):
        return self._username

    @property
    def password(self):
        return self._password

    @property
    def host_url(self):
        return self._host_url


