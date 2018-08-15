import pytest
import os
from utils.utils import (normalize_path, normalize_file_path,
                         determine_build_tool, check_file_in_dir,
                         create_tmp_dir, delete_tmp_dir, TEMP_DIR)


TEST_DIR = os.path.dirname(os.path.abspath(__file__))

class TestUtils(object):
    def test_normalize_path(self):
        x = "/home/user/path/example"
        x_result = "/home/user/path/example/"
        assert normalize_path(x) == x_result
        assert normalize_path(x_result) == x_result


    def test_normalize_file_path(self):
        x = "/home/user/path/example"
        x_result = "/home/user/path/example/"
        assert normalize_file_path(x) == x


    def test_check_file_in_dir(self):
        npm_project = os.path.join(TEST_DIR, 'example/npm_project')
        assert check_file_in_dir(normalize_path(npm_project), 'package.json') == [os.path.join(TEST_DIR, 'example/npm_project/package.json')]


    def test_determine_build_tool(self):
        python_project_path = normalize_path(os.path.join(TEST_DIR, 'example/py_project'))
        py_path_result = (['pip',
                           'pip'],
                          [[],
                           [os.path.join(TEST_DIR, 'example/py_project/requirements.txt')],
                           [os.path.join(TEST_DIR, 'example/py_project/setup.py')]])
        npm_project_path = normalize_path(os.path.join(TEST_DIR, 'example/npm_project'))
        npm_path_result = (['npm'],
                           [[os.path.join(TEST_DIR, 'example/npm_project/package.json')],
                            [],
                            []])
        assert determine_build_tool(npm_project_path) == npm_path_result
        assert determine_build_tool(python_project_path) == py_path_result


    def test_temp_dir(self):
        python_project_path = normalize_path(os.path.join(TEST_DIR, 'example/py_project'))
        temp_dir_path = normalize_path(os.path.join(TEST_DIR, 'example/py_project/{0}'.format(TEMP_DIR)))
        create_tmp_dir(python_project_path)
        assert os.path.isdir(temp_dir_path) == True
        delete_tmp_dir(python_project_path)
