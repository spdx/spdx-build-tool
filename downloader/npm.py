from __future__ import print_function, unicode_literals
import os
import json
import re
import multiprocessing
import aiohttp
import aiofiles
import fasteners
from .utils import npm_utils
from utils.utils import TEMP_DIR, create_tmp_dir, normalize_path, print_to_command_line, is_connected
from .logger import log
import tarfile
import codecs
import collections
import asyncio
from typing import List, Dict


class NpmClient:

    def __init__(self):
        self._session = None

    def connect(self):
        self._session = aiohttp.ClientSession(raise_for_status=True)

    def close(self):
        # self._session.close()
        if not self._session.closed:
            if self._session._connector_owner:
                self._session._connector.close()
            self._session._connector = None

    async def _get_json(self, url: str):
        try:
            log.debug('GET %s', url)
            async with self._session.get(url) as response:
                return await response.json()
        except BaseException:
            log.error('Failed to get JSON from %s', url)
            raise

    async def get_package_latest_version(self, name: str):
        return (await self.get_registry_package_info(name, version='latest'))['version']

    async def get_package_versions(self, name: str):
        content = await self._get_json(npm_utils.build_all_versions_url(name))
        return list(content['versions'].keys())

    async def get_registry_package_info(self, name: str, version: str):
        # NPM Site does not allow /{version} for scoped packages
        if not npm_utils.is_scoped(name):
            return await self._get_json(npm_utils.build_version_url(name, version))
        content = await self._get_json(npm_utils.build_all_versions_url(name))
        return content['versions'][content['dist-tags'][version]]

    async def download_tar_ball_of(self, name: str, version: str, download_dir: str):
        file_name = npm_utils.build_filename(name, version)
        url = npm_utils.build_tarball_url(name, version)
        parent_dir = os.path.join(download_dir, name)
        os.makedirs(parent_dir, exist_ok=True)
        file_path = os.path.join(parent_dir, file_name)
        if os.path.exists(file_path):
            return (file_path, False)
        file_lock = fasteners.InterProcessLock(file_path)
        with fasteners.try_lock(file_lock) as got_file_lock:
            if not got_file_lock:
                return (file_path, False)

            async with self._session.get(url) as response:
                async with aiofiles.open(file_path, 'wb') as file_stream:
                    await npm_utils.copyfileobj(response.content, file_stream)
            return (file_path, True)

    async def get_latest_dependencies_version(self, dependencies: Dict[str, str]) -> Dict[str, str]:
        dependencies_versions = {}
        for package, version in dependencies.items():
            try:
                dependencies_versions[package] = await self.get_latest_satisfying_version(package, version)
            except BaseException:
                log.error('Failed getting %s version', package.name)
        return dependencies_versions

    async def get_latest_satisfying_version(self, name, version) -> str:
        versions = await self.get_package_versions(name)
        return npm_utils.find_lastest_satisfying_version(versions, version)


class NpmPackage:

    PACKAGE_JSON_PATH_PATTERN = re.compile(r'^[^\/]+\/package\.json$')

    __slots__ = ('name', 'version', 'file_path')

    def __init__(self, name: str, version: str, file_path: str):
        self.name = name
        self.version = version
        self.file_path = file_path

    async def get_dependencies(self) -> dict:
        package_info = await self.get_package_json()
        dependencies = {}
        if 'dependencies' in package_info:
            dependencies.update(package_info['dependencies'])
        if 'peerDependencies' in package_info:
            dependencies.update(package_info['peerDependencies'])
        return dependencies

    async def get_package_json(self) -> dict:
        # TODO: Ndip: Correct dependency support
        async with aiofiles.open(self.file_path, "rb") as tar_file:
            tar_mem_stream = io.BytesIO(await tar_file.read())
        with tarfile.open(fileobj=tar_mem_stream, mode='r:gz') as tar_file:
            for internal_path in tar_file.getnames():
                if not NpmPackage.PACKAGE_JSON_PATH_PATTERN.match(
                        internal_path):
                    continue
                member = tar_file.getmember(internal_path)
                with tar_file.extractfile(member) as file_stream:
                    return NpmPackage.parse_package_json(file_stream)
        return {}

    @staticmethod
    def parse_package_json(file_stream):
        data = file_stream.read()
        if data.startswith(codecs.BOM_UTF8):
            encoded_data = data.decode('utf-8-sig')
        else:
            encoded_data = data.decode('utf-8')
        return json.loads(encoded_data)


class NpmPackageDownloader:

    def __init__(self, max_tasks: int=10):
        self._client = NpmClient()
        self._download_dir = TEMP_DIR
        self._max_tasks = max_tasks
        create_tmp_dir()

    async def _download_single_package(self, name: str, version: str=None) -> (NpmPackage, bool):
        try:
            name = npm_utils.normalize_package(name)
            if version is None:
                log.info('Downloading %s', name)
                version = await self._client.get_package_latest_version(name)
            else:
                log.info('Downloading %s@%s', name, version)
            file_path, was_downloaded = await self._client.download_tar_ball_of(name, version, self._download_dir)
            package_info = NpmPackage(
                name=name, version=version, file_path=file_path)
            return package_info, was_downloaded
        except BaseException:
            log.error('Error downloading %s', name)
            return (None, False)

    async def _get_package_latest_dependencies(self, package: NpmPackage) -> Dict[str, str]:
        try:
            required_dependencies = await package.get_dependencies()
            normalized_dependencies = {
                npm_utils.normalize_package(k): v for k,
                v in required_dependencies.items()}
            return await self._client.get_latest_dependencies_version(normalized_dependencies)
        except BaseException:
            log.error('Error getting %s dependencies', package.name)
            return {}

    async def download_packages(self, packages: List[NpmPackage]):
        self._client.connect()
        package_queue = collections.deque(packages)

        current_packages = npm_utils.multi_pop(package_queue, self._max_tasks)
        tasks = [self._download_single_package(
            n, v) for n, v in current_packages]
        while tasks:
            tasks_done, tasks_pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
            for task in tasks_done:
                package, was_downloaded = task.result()
                if not was_downloaded:
                    continue
                dependencies = await self._get_package_latest_dependencies(package)
                for sub_package, sub_package_version in dependencies.items():
                    package_queue.appendleft(
                        (sub_package, sub_package_version))
            additional_packages = npm_utils.multi_pop(
                package_queue, min(len(tasks_done), self._max_tasks))
            tasks_pending.update([self._download_single_package(n, v)
                                  for n, v in additional_packages])
            tasks = tasks_pending
        self._client.close()

    def download_multiple(self, packages: List[NpmPackage]):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.download_packages(packages))

    def download(self, name: str, version: str=None):
        self.download_multiple([(name, version)])


class MultiPackageDownloader:

    _PACKAGE_WITH_VERSION_PATTERN = re.compile(r'^(.+)@(.+)$')

    def __init__(self, project_dir, package_list: str, num_of_workers: int):
        self._download_dir = '{0}{1}'.format(
            normalize_path(project_dir), TEMP_DIR)
        self._num_of_workers = num_of_workers
        self._workers = []
        self._package_groups = list(self._group_packages(package_list))
        create_tmp_dir(self.project_dir)

    def _group_packages(self, package_list: str):
        packages = package_list
        package_groups = [[] for _ in range(self._num_of_workers)]
        for i, package in enumerate(packages):
            package_groups[i % self._num_of_workers].append(package)
        for group in package_groups:
            yield [package for package in group]

    def start(self):
        self._workers = []
        for i in range(self._num_of_workers):
            worker = multiprocessing.Process(
                target=self._packages_downloader,
                args=(self._package_groups[i], self._download_dir))
            worker.start()
            self._workers.append(worker)

    def wait(self):
        for i in self._workers:
            i.join()

    @staticmethod
    def _packages_downloader(packages, download_dir):
        package_downloader = NpmPackageDownloader()
        if is_connected():
            package_downloader.download_multiple(packages)
        else:
            print_to_command_line("You are not online, we cannot download project dependencies. You need to be online.", "failure")
            return
