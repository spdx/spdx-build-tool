import pytest
import os
from utils.utils import (determine_build_tool,
normalize_path, normalize_file_path)
from analyser.managers.npm import NpmPackageManager
from analyser.managers.pip import PipPackageManager

TEST_DIR = os.path.dirname(os.path.abspath(__file__))

class TestAnalyser(object):
    def test_npm_analyser(self):
        npm_project_path = normalize_path(os.path.join(TEST_DIR, 'example/npm_project'))
        project_info = determine_build_tool(normalize_path(npm_project_path))
        package_json_path = normalize_file_path(os.path.join(TEST_DIR, 'example/npm_project/package.json'))
        assert "npm" in project_info[0]
        pkg_mgr = NpmPackageManager(normalize_path(npm_project_path), True)
        assert pkg_mgr.project_dir == normalize_path(os.path.join(TEST_DIR, 'example/npm_project'))
        assert pkg_mgr.in_tests == True
        assert pkg_mgr.files_to_parse == [[package_json_path]]


    def test_pip_analyser(self):
        python_project_path = normalize_path(os.path.join(TEST_DIR, 'example/py_project'))
        project_info = determine_build_tool(normalize_path(python_project_path))
        requirements_file_path = normalize_file_path(os.path.join(TEST_DIR, 'example/py_project/requirements.txt'))
        assert "pip" in project_info[0]
        pkg_mgr = PipPackageManager(normalize_path(python_project_path), True)
        assert pkg_mgr.project_dir == normalize_path(os.path.join(TEST_DIR, 'example/py_project'))
        assert pkg_mgr.in_tests == True
        assert pkg_mgr.files_to_parse == [[requirements_file_path]]
