#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Downloader entry point"""

from __future__ import print_function

import argparse
import sys
from .npm import MultiPackageDownloader, NpmPackageDownloader
from .pip import PipPkgDownloader



def main(argv):
    """Analyser entry point.

    :param argv: command-line arguments
    :type argv: :class:`list`
    """
    # First argument must be the project directory
    # print("argv", argv)
    # downloader = NpmPackageDownloader()
    # downloader.download('react', version='15.4.1')
    req_file_dir = '/home/mikael/Desktop/projects/magazine_env/magazine/backend/requirements.txt'
    downloader = PipPkgDownloader(req_file_dir, "")
    return


def entry_point():
    """Zero-argument entry point for use with setuptools/distribute."""
    raise SystemExit(main(sys.argv))


if __name__ == '__main__':
    entry_point()
