#!/bin/bash

sphinx-apidoc -o docs/source/ saucedemo_selenium_lib/
cd docs
make html

