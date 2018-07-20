from __future__ import print_function, unicode_literals
from utils.utils import SUPPORTED_BUILD_TOOLS, determine_build_tool, check_file_in_dir, print_to_command_line, FILES_TO_PARSE_PER_TOOL, normalize_path, normalize_file_path, TEMP_DIR
from analyser.parsers.npm import NpmFileParser
from downloader.npm import MultiPackageDownloader, NpmPackageDownloader
from scanner.main import PkgScanner


class NpmPackageManager(object):
    """
    Package manager class for npm packages.
    Recieves a single project dir as input,
    """

    def __init__(self, project_dir):
        # Do not call this private method
        self.project_dir = project_dir
        self.files_to_check = FILES_TO_PARSE_PER_TOOL["npm"]
        self.files_to_parse = []
        self.json_obj = None
        self.get_files_to_parse()

    def get_files_to_parse(self):
        print_to_command_line("Project directory", "title")
        print_to_command_line(self.project_dir, "success")
        for file_name_to_check in self.files_to_check:
            self.files_to_parse.append(check_file_in_dir(self.project_dir, file_name_to_check))
        self.parse_npm_file()

    def parse_npm_file(self):
        # @TODO: Correct this
        """Just parsing the first package.json file."""
        self.json_obj = NpmFileParser(self.files_to_parse[0][0])
        # print("self.json_obj dependencies", self.json_obj.dependencies)
        # print("self.json_obj devDependencies", self.json_obj.devDependencies)
        dep_list = []
        if self.json_obj.dependencies:
            dep_list = dep_list + list(self.json_obj.dependencies.items())
        if self.json_obj.devDependencies:
            dep_list = dep_list + list(self.json_obj.devDependencies.items())
        self.download_npm_pkg(dep_list)

    def download_npm_pkg(self, dep_list):
        downloader = MultiPackageDownloader(self.project_dir, dep_list, 15)
        # print("downloader", downloader._package_groups)
        downloader.start()
        self.scan_pkg(self.project_dir)

    def scan_pkg(self, pkg_dir):
        scanner = PkgScanner(pkg_dir)
