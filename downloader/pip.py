from __future__ import absolute_import

import logging
import os
from utils.utils import TEMP_DIR, create_tmp_dir, normalize_path, is_connected, print_to_command_line

logger = logging.getLogger(__name__)


class PipPkgDownloader:
    """
    Download packages from requirements file"""

    def __init__(self, req_file, project_dir, pkg_name):

        self.req_file = req_file
        self.pkg_name = pkg_name
        self.dest_dir = '{0}{1}'.format(normalize_path(project_dir), TEMP_DIR)
        self.download_output = None
        create_tmp_dir(project_dir)
        self.download()

    def download(self):
        # Create setup file before downloading the packages to a directory
        touch_cmd = "touch {0}setup.py".format(normalize_path(self.dest_dir))
        # Run the Command
        if is_connected():
            cmd_output = os.popen(
                "pip download -r {0} -d {1}".format(self.req_file, self.dest_dir)).read()
            # delete setup file after packages have been downloaded
            os.popen("rm -f {0}setup.py".format(self.dest_dir))
            self.download_output = cmd_output
            return cmd_output
        else:
            print_to_command_line("You are not online, we cannot download project dependencies. You need to be online.", "failure")
            return
