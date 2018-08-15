from __future__ import print_function, unicode_literals
from utils.utils import (check_file_in_dir, print_to_command_line,
                        FILES_TO_PARSE_PER_TOOL)
from analyser.parsers.pip import PipFileParser
from downloader.pip import PipPkgDownloader
from scanner.main import PkgScanner


class PipPackageManager(object):
    """
    Package manager class for pip packages.
    Recieves a single project dir as input,
    """

    def __init__(self, project_dir, in_tests=False):
        # Do not call this private method
        self.project_dir = project_dir
        self.in_tests = in_tests
        self.files_to_check = FILES_TO_PARSE_PER_TOOL["pip"]
        self.files_to_parse = []
        self.json_obj = None
        self.get_files_to_parse()

    def get_files_to_parse(self):
        if not self.in_tests:
            print_to_command_line("Project directory", "title")
            print_to_command_line(self.project_dir, "information")
        for file_name_to_check in self.files_to_check:
            self.files_to_parse.append(
            check_file_in_dir(self.project_dir, file_name_to_check))
        self.parse_pip_file()

    def parse_pip_file(self):
        # @TODO: Correct this
        """Just parsing the first requirements.txt file."""
        self.json_obj = PipFileParser(self.files_to_parse[0][0], self.in_tests)
        if not self.in_tests:
            self.download_pip_pkg(self.json_obj.file_dir)

    def download_pip_pkg(self, req_file_dir):
        PipPkgDownloader(req_file_dir, self.project_dir, "")
        # print("downloader output", downloader.download_output)
        self.scan_pkg(self.project_dir)
        return

    def scan_pkg(self, pkg_dir):
        PkgScanner(pkg_dir)
