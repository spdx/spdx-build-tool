from __future__ import print_function, unicode_literals
from __future__ import unicode_literals
import glob
import fnmatch
import os
import json
import warnings
import re
from utils.utils import (print_to_command_line, normalize_file_path,
                        normalize_path)


class NpmFileParser(object):
    """
    Parser class for npm packages.
    Recieves a single package.json file dir as input,
    and parses it to return the dependencies, alongside valuable info.
    """

    def __init__(self, file_dir):
        # Do not call this private method
        self.file_dir = normalize_file_path(file_dir)
        self.node_modules_dir = None
        self.name = None
        self.version = None
        self.license = None
        self.dependencies = None
        self.devDependencies = None
        self.vcs_fom_package_json = None
        self.set_json_info()
        self.node_modules_dir_for_package_json()

    def parse_file(self):
        print_to_command_line("File path", "title")
        print_to_command_line(self.file_dir, "information")
        package_json_content = None
        with open(self.file_dir) as json_data:
            json_deps_data = json.load(json_data)
            package_json_content = json_deps_data
        return package_json_content

    def set_json_info(self):
        json_info = self.parse_file()
        if 'name' in json_info:
             self.name = json_info["name"]
        if 'version' in json_info:
            self.version = json_info["version"]
        if 'license' in json_info:
            self.license = json_info["license"]
        if 'dependencies' in json_info:
            self.dependencies = json_info["dependencies"]
        if 'devDependencies' in json_info:
            self.devDependencies = json_info["devDependencies"]
        return

    def node_modules_dir_for_package_json(self):
        if self.file_dir:
            dir_list = self.file_dir.split('/')
            parent_dir = '/'.join(dir_list[:-1])
            for name in os.listdir(parent_dir):
                if os.path.isdir('{0}/{1}'.format(parent_dir, name)):
                    if name == "node_modules":
                        self.node_modules_dir = normalize_path('{0}/{1}'.format(
                        parent_dir, name))
