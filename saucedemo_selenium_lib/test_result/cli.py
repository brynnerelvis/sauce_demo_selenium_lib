""" TEST RESULT CLI
Command Interface for running tests

"""
import os
import time
from typing import Dict

import click
from pathlib import Path

from saucedemo_selenium_lib.test_result.runner import SaucedemoTestRunner, SaucedemoPipelineTestRunner

LIB_BASE_PATH = os.path.abspath(os.path.join(__file__, "../../../"))


def print_targets(targets: Dict):
    click.echo("Available tests to deploy")
    print("---------------------------------")
    click.echo("Index      Name")

    for index, target in targets.items():
        click.echo(f"{index}            {target}")


def get_targets(targets_path):
    """Get dir banes of all targets in targets_path"""
    p = Path(targets_path)
    counter = 1
    targets = {}
    for path in p.iterdir():
        if path.is_dir() and not path.name.startswith("__"):
            targets[str(counter)] = path.name
            counter += 1

    return targets


@click.option(
    "--load-scope",
    is_flag=True,
    help="Set this when running a specific target if you want each test case class tests to run in one processes. "
    "Generally, targets tests to be run with load-scope options are set in "
    "./saucedemo_integration-test-selenium-lib/saucedemo_selenium_lib/test_result/runner.py::SaucedemoTestRunner.LOAD_SCOPE_TARGETS",
)
@click.option(
    "--browser",
    help="Browser in to run tests. Available options include 'chrome' and 'firefox'",
    default="chrome",
    type=str,
    show_default=True,
)
@click.option(
    "--num-procs",
    help="Number of processes to run run tests in parallel. You can set 'NUM_PROCS' envar once to your own designed "
    "number of processes",
    default=lambda: int(os.environ.get("NUM_PROCS", 5)),
    type=int,
    show_default=True,
)
@click.option("--run-all", is_flag=True, help="Run all tests")
@click.option(
    "--headless",
    default=1,
    help="Run tests in headless mode by setting headless to 1. Headless means the browser will not be open when "
    "running tests",
)
@click.option(
    "--host-index",
    help="Index of a Host in config File. You can set 'HOST_INDEX' envar to avoid setting it in every run. The config "
    "file is expected in Test Result base dir. If you have different path of the config file, set 'CONFIG_PATH' "
    "envar. This allow using one config file in different test projects",
    default=lambda: int(os.environ.get("HOST_INDEX", 0)),
    type=int,
    show_default=True,
)
@click.option(
    "--target",
    default=None,
    help="Target to be run. Set this if you want to run specific targets",
    show_default=True,
)
@click.option(
    "--test-results-path",
    default=Path(LIB_BASE_PATH).parent,
    type=click.Path(exists=True),
    help="Base Dir for test-results repo",
    show_default=True,
)
@click.option(
    "--grid",
    help="Url of the grid to run the test, if it isn't defined the test will run locally",
    default=None,
    show_default=True,
)
@click.option(
    "--url",
    help="Url where the test are going to run",
    default=None,
    show_default=True,
)
@click.option(
    "--username",
    help="Username of the given host",
    default=None,
    show_default=True,
)
@click.option(
    "--password",
    help="Password of the given user",
    default=None,
    show_default=True,
)
@click.command()
def run_tests(
    test_results_path,
    target,
    run_all,
    host_index,
    headless,
    num_procs,
    browser,
    load_scope,
    grid,
    url=None,
    username=None,
    password=None,
):
    """Command for running tests

    To make this command executable in a python module e.g with python 'run_tests.py'
    call it in if __name__ == "__main__": of run_tests.py of test_results repo

    Example:

        if __name__ == "__main__":
            run_tests()


    """
    click.echo(f"Running tests for Base Path:- {Path(test_results_path).name}")

    click.echo(target)
    targets_path = os.path.join(test_results_path, "tests")
    targets = get_targets(targets_path)
    load_scope_targets = []
    if target:
        targets_to_run = [target]
        if load_scope:
            load_scope_targets.append(target)
    elif run_all:
        targets_to_run = list(targets.values())
    else:
        print_targets(targets)

        index = click.prompt(
            "Choose Targets",
            type=click.Choice(targets),
            show_choices=False,
        )
        targets_to_run = [targets[index]]
    click.echo(f"Running tests for target: {targets_to_run}")

    start_time = time.time()
    output_path = os.path.join(test_results_path, "output")

    if url is not None and username is not None and password is not None:
        click.echo(f"Running tests using SaucedemoPipelineTestRunner")
        test_runner = SaucedemoPipelineTestRunner(
            targets_path,
            targets_to_run,
            url,
            username,
            password,
            headless=headless,
            output_path=output_path,
            num_processes=num_procs,
            load_scope_targets=load_scope_targets,
            browser=browser,
            grid=grid,
        )
    else:
        click.echo(f"Running tests using SaucedemoTestRunner")
        test_runner = SaucedemoTestRunner(
            targets_path,
            targets_to_run,
            host_index=host_index,
            headless=headless,
            output_path=output_path,
            num_processes=num_procs,
            load_scope_targets=load_scope_targets,
            browser=browser,
            grid=grid,
        )

    test_runner.run()

    print(f"--- duration {(time.time() - start_time) / 3600} Hours ---")
