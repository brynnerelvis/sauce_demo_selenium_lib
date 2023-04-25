import os
from datetime import datetime
import hashlib


def md5_hash_file_content(file_name, chunk_size=4096):
    hash_md5 = hashlib.md5()
    with open(file_name, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def create_unique_string(phrase, str_format="%Y-%m-%d %H:%M:%S.%f"):
    """Add timestamp  to a given phrase to create a unique string."""
    date_time = datetime.now().strftime(str_format)
    return f"{phrase}-{date_time}"


def get_current_running_test_full_name():
    """Return file name, Test case class and test of current executing test in form of
    <test_file>-<Test case Class>-<test name>. Intended for debugging and save screen shoots"""
    # Pytest automatically set envar PYTEST_CURRENT_TEST. There are cases where it might be set correctly especially when running test
    test_info = os.environ.get("PYTEST_CURRENT_TEST")

    if test_info is None:
        raise ValueError("PYTEST_CURRENT_TEST value is None")
    test_info = test_info.replace("::", "-")  # replace :: with -
    test_info = test_info.replace(".py", "")  # remove .py
    return test_info


def create_folder_if_non_exist(folder_path):
    """
    Create a folder if the given folder path does not exist

    """
    if not os.path.exists(folder_path):
        print(f"Folder: {folder_path} does not exist")
        print(f"Creating a folder: {folder_path}")
        os.mkdir(folder_path)
