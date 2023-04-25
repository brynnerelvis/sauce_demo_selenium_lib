from setuptools import setup, find_packages

setup(
    name="saucedemo_selenium_lib",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "selenium~=4.8.1.0",
        "pytest~=6.2.5",
        "PyYAML~=5.4.1",
        "lxml~=4.6.2",
        "openpyxl~=3.0.4",
        "pytest-xdist~=2.2.0",
        "pytest-html~=2.1.1",
        "click~=8.0.3",
        "webdriver-manager~=3.8.5",
    ],
)
