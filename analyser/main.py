#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Analyser entry point"""

from __future__ import print_function

import argparse
import sys
from utils.utils import (determine_build_tool,
normalize_path, print_to_command_line)
from analyser.managers.npm import NpmPackageManager
from analyser.managers.pip import PipPackageManager
from setup import setup_dict


def analyse_dir(verbose, package_dir):
    npm_deps = []
    project_info = determine_build_tool(normalize_path(package_dir))
    if "npm" in project_info[0]:
        print_to_command_line("NPM Project", "success")
        NpmPackageManager(normalize_path(package_dir))
    if "pip" in project_info[0]:
        print_to_command_line("Python Project", "success")
        PipPackageManager(normalize_path(package_dir))
    return project_info


def main(argv):
    """Analyser entry point.

    :param argv: command-line arguments
    :type argv: :class:`list`
    """
    # First argument must be the project directory
    print("argv", argv)
    return analyse_dir(True, argv[1])
    # epilog = '''
    #         {project} {version}
    #
    #         {authors}
    #         URL: <{url}>
    #         '''.format(
    #     project=setup_dict['name'],
    #     version=setup_dict['version'],
    #     authors=setup_dict['author'],
    #     url=setup_dict['url'])
    # arg_parser = argparse.ArgumentParser(
    #     prog=argv[0],
    #     formatter_class=argparse.RawDescriptionHelpFormatter,
    #     description=setup_dict['description'],
    #     epilog=epilog)
    # arg_parser.add_argument(
    #     '-V', '--version',
    #     action='version',
    #     help='Display the project\'s version',
    #     version='{0} {1}'.format(setup_dict['name'], setup_dict['version']))
    # arg_parser.add_argument(
    #     '-I',
    #     '--info',
    #     action='version',
    #     help='Display the project\'s readme content',
    #     version='{0} {1}'.format(
    #         setup_dict['name'],
    #         setup_dict['long_description']))
    #
    # arg_parser.parse_args(args=argv[1:])
    # return analyse_dir(True, argv[1])
    # pass


def entry_point():
    """Zero-argument entry point for use with setuptools/distribute."""
    raise SystemExit(main(sys.argv))


if __name__ == '__main__':
    entry_point()
