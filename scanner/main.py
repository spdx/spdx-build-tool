#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Scanner entry point"""

from __future__ import print_function

import sys
import os
from utils.utils import print_to_command_line, delete_tmp_dir, TEMP_DIR, normalize_path, is_connected, SCANCODE_DOWNLOAD_PATH
import zipfile
from setup import ROOT_DIR
import subprocess
import socket


class PkgScanner:
    """Package scanner helper class"""

    def __init__(self, directory_to_scan):
        self.directory_to_scan = directory_to_scan
        self.SCANCODE_PATH = os.path.join(ROOT_DIR, 'scancode-toolkit-2.2.1')
        self.EXTRACT_CODE_PATH = ''
        self.CONFIG_PATH = ''
        self.SCANCODE_EXE_PATH = ''
        self.download_scancode()


    def download_scancode(self):
        download_command = "pip download {0} --no-deps".format(
            SCANCODE_DOWNLOAD_PATH)
        scancode_exists = os.path.exists(self.SCANCODE_PATH)
        if not scancode_exists:
            if is_connected():
                os.popen(download_command).read()
                zip_ref = zipfile.ZipFile("scancode-toolkit-2.2.1.zip", 'r')
                zip_ref.extractall(".")
                zip_ref.close()
            else:
                print_to_command_line("You are not online, we cannot download scanner utilites. You need to be online for the first run.", "failure")
                return
        self.EXTRACT_CODE_PATH = os.path.join(
            self.SCANCODE_PATH, 'extractcode')
        self.CONFIG_PATH = os.path.join(self.SCANCODE_PATH, 'configure')
        self.SCANCODE_EXE_PATH = os.path.join(self.SCANCODE_PATH, 'scancode')
        # make extractcode executable
        os.popen("chmod 777 {0}".format(self.EXTRACT_CODE_PATH)).read()
        os.popen("chmod 777 {0}".format(self.CONFIG_PATH)).read()
        os.popen("chmod 777 {0}".format(self.SCANCODE_EXE_PATH)).read()
        self.extract_content_of_temp_dir()
        self.scan()

    def extract_content_of_temp_dir(self):
        temp_directory = '{0}{1}'.format(
            normalize_path(self.directory_to_scan), TEMP_DIR)
        os.chdir(os.path.abspath(self.SCANCODE_PATH))
        for filename in os.listdir(temp_directory):
            extract_str = "./extractcode {0}{1}{2}".format(
                normalize_path(self.directory_to_scan),
                normalize_path(TEMP_DIR), filename)
            os.popen(extract_str).read()
        return

    def scan(self):
        """Scan given directory, and output the result as an spdx document in the directory being scanned."""
        print_to_command_line("directory to scan", "title")
        print_to_command_line(self.directory_to_scan, "success")
        os.chdir(os.path.abspath(self.SCANCODE_PATH))
        ignore_pattern = "**/NO-DIRECTORY/**"
        spdx_rdf_filename = '{0}{1}-build-tool-rdf.spdx'.format(
            self.directory_to_scan, self.directory_to_scan.split("/")[-2])
        spdx_tv_filename = '{0}{1}-build-tool-tv.spdx'.format(
            self.directory_to_scan, self.directory_to_scan.split("/")[-2])
        rdf_scan_str = "./scancode --format spdx-rdf  {0} {1} --ignore {2}".format(
            self.directory_to_scan, spdx_rdf_filename, ignore_pattern)
        tv_scan_str = "./scancode --format spdx-tv  {0} {1} --ignore {2}".format(
            self.directory_to_scan, spdx_tv_filename, ignore_pattern)
        os.popen(rdf_scan_str).read()
        os.popen(tv_scan_str).read()
        delete_tmp_dir(self.directory_to_scan)


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
