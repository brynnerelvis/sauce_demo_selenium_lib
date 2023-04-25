import glob
import os
import time

from saucedemo_selenium_lib.exceptions import SaucedemoTestError
from saucedemo_selenium_lib.saucedemo_utils.saucedemo_utils import SaucedemoUtils


class SaucedemoFileDownloader:
    """For downloading files to a given path"""

    def __init__(self, suacedemo_utils, download_button_locator, download_path):
        self._saucedemo_utils: SaucedemoUtils = suacedemo_utils
        self._download_button_locator = download_button_locator
        self._download_path = download_path
        self._downloaded_file = None

    def _enable_download_headless(self):
        """Control the headless downlolad to a specific download path"""
        self._saucedemo_utils.driver.command_executor._commands["send_command"] = (
            "POST",
            "/session/$sessionId/chromium/send_command",
        )
        params = {
            "cmd": "Page.setDownloadBehavior",
            "params": {"behavior": "allow", "downloadPath": self._download_path},
        }
        self._saucedemo_utils.driver.execute("send_command", params)

    def _get_latest_created_file(self):
        all_files = glob.glob(os.path.join(self._download_path, "*"))
        if len(all_files) == 0:
            raise FileNotFoundError(f"File not found in {self._download_path} ")
        downloaded_file = max(
            all_files, key=os.path.getctime
        )  # return the latest downloaded file
        print(f"Latest downloaded file : {downloaded_file}")
        return downloaded_file

    def get_downloaded_file(self):
        """Ge the downloaded file path"""
        if self._downloaded_file is None:
            raise ValueError(f"File is not downloaded")
        return self._downloaded_file

    def _get_file_creation_time(self, file):
        try:
            file_creation_time = os.path.getmtime(filename=file)
            return file_creation_time
        except FileNotFoundError:
            return 0

    def download(self, time_out=60):
        """Download a file to a given download path."""
        download_start_time = time.time()
        self._saucedemo_utils.click_at_element(self._download_button_locator)
        wait_second = 2
        total_wait = 0

        while True:
            try:

                downloaded_file = self._get_latest_created_file()
                file_creation_time = self._get_file_creation_time(downloaded_file)

                if (
                    file_creation_time < download_start_time
                    or downloaded_file.endswith(".crdownload")
                    or downloaded_file.endswith(".part")
                ):
                    pass

                else:
                    self._saucedemo_utils.logger.info(
                        f"Download complete for file: {downloaded_file}"
                    )
                    self._downloaded_file = downloaded_file
                    return downloaded_file
            except FileNotFoundError:
                print(f"No file in folder: {self._download_path}")
            finally:
                time.sleep(wait_second)
                total_wait += wait_second
                self._saucedemo_utils.logger.info("Downloading ....")
            if total_wait > time_out:
                raise SaucedemoTestError(
                    "Download  timeout. File couldn't be downloaded"
                )
