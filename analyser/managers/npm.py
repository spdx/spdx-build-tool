from __future__ import print_function, unicode_literals
from utils.utils import (check_file_in_dir, print_to_command_line,
                        FILES_TO_PARSE_PER_TOOL)
from analyser.parsers.npm import NpmFileParser
from downloader.main import MultiPackageDownloader
from scanner.main import PkgScanner


class NpmPackageManager(object):
    """
    Package manager class for npm packages.
    Recieves a single project dir as input,
    """

    def __init__(self, project_dir, in_tests=False):
        # Do not call this private method
        self.project_dir = project_dir
        self.in_tests = in_tests
        self.files_to_check = FILES_TO_PARSE_PER_TOOL["npm"]
        self.files_to_parse = []
        self.json_obj = None
        self.dep_list = None
        self.get_files_to_parse()

    def get_files_to_parse(self):
        if not self.in_tests:
            print_to_command_line("Project directory", "title")
            print_to_command_line(self.project_dir, "success")
        for file_name_to_check in self.files_to_check:
            self.files_to_parse.append(
            check_file_in_dir(self.project_dir, file_name_to_check))
        self.parse_npm_file()

    def parse_npm_file(self):
        # @TODO: Correct this
        """Just parsing the first package.json file."""
        self.json_obj = NpmFileParser(self.files_to_parse[0][0], self.in_tests)
        dep_list = []
        if self.json_obj.dependencies:
            dep_list = dep_list + list(self.json_obj.dependencies.items())
        if self.json_obj.devDependencies:
            dep_list = dep_list + list(self.json_obj.devDependencies.items())
        self.dep_list = dep_list
        if not self.in_tests:
            self.download_npm_pkg(dep_list)

    def download_npm_pkg(self, dep_list):
        print("dep_list")
        print(dep_list)
        downloader = MultiPackageDownloader(self.project_dir, dep_list, 10)
        # print("downloader", downloader._package_groups)
        # downloader.start()
        # downloader.wait()
        # self.scan_pkg(self.project_dir)

    def scan_pkg(self, pkg_dir):
        PkgScanner(pkg_dir)
