#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Scanner entry point"""

from __future__ import print_function

import sys
import os
from utils.utils import (create_tmp_dir, print_to_command_line, delete_tmp_dir,
                         TEMP_DIR, normalize_path, is_connected, SCANCODE_DOWNLOAD_PATH)
import zipfile
from setup import ROOT_DIR
import distutils
from distutils import dir_util


class MultiPackageDownloader:
    """Package downloader helper class"""

    def __init__(self, directory_to_scan, pkg_list, num_workers=10):
        self.directory_to_scan = directory_to_scan
        self.pkg_list = pkg_list
        self.download_dir = '{0}{1}'.format(
            normalize_path(self.directory_to_scan), TEMP_DIR)
        self.node_modules_dir = '{0}node_modules'.format(
            normalize_path(self.directory_to_scan))
        create_tmp_dir(self.directory_to_scan)
        self.create_dep_file()


    def create_dep_file(self):
        file_to_write = '{0}pkg_list.txt'.format(
            normalize_path(self.download_dir))
        pkg_list_file = open(file_to_write, 'w+')
        for item in self.pkg_list:
            if os.path.exists(self.node_modules_dir):
                if not self.check_if_pkg_exists(item[0]):
                    pkg_list_file.write("{0}@{1}\n".format(item[0], item[1]))
            else:
                pkg_list_file.write("{0}@{1}\n".format(item[0], item[1]))
        pkg_list_file.close()


    def copy_pkg_to_temp(self, pkg_name):
        """Copy package directory to temp directory"""
        src_dir = '{0}{1}'.format(
            normalize_path(self.node_modules_dir), pkg_name)
        dest_dir = '{0}{1}'.format(
            normalize_path(self.download_dir), pkg_name)
        distutils.dir_util.copy_tree(src_dir, dest_dir)


    def check_if_pkg_exists(self, pkg_name):
        """Checks if the package exists in the node_modules folder.
        If it does, it copies it to the temp_directory, if not, it adds it to the download list"""
        item_dir = '{0}{1}/'.format(
            normalize_path(self.node_modules_dir), pkg_name)
        pkg_exists = os.path.exists(item_dir)
        if pkg_exists:
            self.copy_pkg_to_temp(pkg_name)
        return pkg_exists



def main(argv):
    """scanner entry point.

    :param argv: command-line arguments
    :type argv: :class:`list`
    """
    return


def entry_point():
    """Zero-argument entry point for use with setuptools/distribute."""
    raise SystemExit(main(sys.argv))


if __name__ == '__main__':
    entry_point()
