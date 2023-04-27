from setuptools import setup, find_packages

setup(
    name="saucedemo_selenium_lib",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "selenium~=4.8.1.0",
        "pytest==7.3.1",
        "PyYAML==6.0",
        "lxml==4.9.2",
        "openpyxl==3.1.2",
        "pytest-xdist~=2.2.0",
        "pytest-html~=2.1.1",
        "click==8.1.3",
        "webdriver-manager~=3.8.5",
    ],
)
