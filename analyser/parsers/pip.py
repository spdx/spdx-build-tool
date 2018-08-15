from __future__ import print_function, unicode_literals
import os
import warnings
import re
from utils.utils import print_to_command_line


class PipFileParser(object):
    """
    Parser class for npm packages.
    Recieves a single requirement.txt file dir as input,
    and parses it to return the dependencies, alongside valuable info.
    """

    def __init__(self, file_dir, in_tests=False):
        # Do not call this private method
        self.file_dir = file_dir
        self.setup_file = None
        self.in_tests = in_tests
        self.name = None
        self.version = None
        self.license = None
        self.dependencies = None
        self.devDependencies = None
        self.set_pip_info()

    def parse_file(self):
        if not self.in_tests:
            print_to_command_line("File path", "title")
            print_to_command_line(self.file_dir, "success")
        try:
            # Python 2.x compatibility
            if not isinstance(self.file_dir, basestring):
                self.file_dir = self.file_dir.read()
        except NameError:
            # Python 3.x only
            if not isinstance(self.file_dir, str):
                self.file_dir = self.file_dir.read()
        for line in self.file_dir.splitlines():
            line = line.strip()
        return

    def get_setup_file(self):
        """Gets the setup file in this directory; if it exists"""

    def parse_setup_file(self):
        """Parse the setup.py file"""

    def set_pip_info(self):
        self.parse_file()
        return


VCS = [
    'git',
    'hg',
    'svn',
    'bzr',
]

VCS_SCHEMES = [
    'git',
    'git+https',
    'git+ssh',
    'git+git',
    'hg+http',
    'hg+https',
    'hg+static-http',
    'hg+ssh',
    'svn',
    'svn+svn',
    'svn+http',
    'svn+https',
    'svn+ssh',
    'bzr+http',
    'bzr+https',
    'bzr+ssh',
    'bzr+sftp',
    'bzr+ftp',
    'bzr+lp',
]
URI_REGEX = re.compile(
    r'^(?P<scheme>https?|file|ftps?)://(?P<path>[^#]+)'
    r'(#(?P<fragment>\S+))?'
)

VCS_REGEX = re.compile(
    r'^(?P<scheme>{0})://'.format(r'|'.join(
        [scheme.replace('+', r'\+') for scheme in VCS_SCHEMES])) +
    r'((?P<login>[^/@]+)@)?'
    r'(?P<path>[^#@]+)'
    r'(@(?P<revision>[^#]+))?'
    r'(#(?P<fragment>\S+))?'
)

# This matches just about everyting
LOCAL_REGEX = re.compile(
    r'^((?P<scheme>file)://)?'
    r'(?P<path>[^#]+)' +
    r'(#(?P<fragment>\S+))?'
)

# Copied from pip
# https://github.com/pypa/pip/blob/281eb61b09d87765d7c2b92f6982b3fe76ccb0af/pip/index.py#L947
HASH_ALGORITHMS = set(['sha1', 'sha224', 'sha384', 'sha256', 'sha512', 'md5'])

extras_require_search = re.compile(
    r'(?P<name>.+)\[(?P<extras>[^\]]+)\]').search


def parse_fragment(fragment_string):
    """Takes a fragment string nd returns a dict of the components"""
    fragment_string = fragment_string.lstrip('#')

    try:
        return dict(
            key_value_string.split('=')
            for key_value_string in fragment_string.split('&')
        )
    except ValueError:
        raise ValueError(
            'Invalid fragment string {fragment_string}'.format(
                fragment_string=fragment_string
            )
        )


def get_hash_info(d):
    """Returns the first matching hashlib name and value from a dict"""
    for key in d.keys():
        if key.lower() in HASH_ALGORITHMS:
            return key, d[key]

    return None, None


def parse_extras_require(egg):
    if egg is not None:
        match = extras_require_search(egg)
        if match is not None:
            name = match.group('name')
            extras = match.group('extras')
            return name, [extra.strip() for extra in extras.split(',')]
    return egg, []


class Requirement(object):
    """
    Represents a single requirement
    Typically instances of this class are created with ``Requirement.parse``.
    For local file requirements, there's no verification that the file
    exists. This class attempts to be *dict-like*.
    See: http://www.pip-installer.org/en/latest/logic.html
    **Members**:
    * ``line`` - the actual requirement line being parsed
    * ``editable`` - a boolean whether this requirement is "editable"
    * ``local_file`` - a boolean whether this requirement is a local file/path
    * ``specifier`` - a boolean whether this requirement used a requirement
      specifier (eg. "django>=1.5" or "requirements")
    * ``vcs`` - a string specifying the version control system
    * ``revision`` - a version control system specifier
    * ``name`` - the name of the requirement
    * ``uri`` - the URI if this requirement was specified by URI
    * ``subdirectory`` - the subdirectory fragment of the URI
    * ``path`` - the local path to the requirement
    * ``hash_name`` - the type of hashing algorithm indicated in the line
    * ``hash`` - the hash value indicated by the requirement line
    * ``extras`` - a list of extras for this requirement
      (eg. "mymodule[extra1, extra2]")
    * ``specs`` - a list of specs for this requirement
      (eg. "mymodule>1.5,<1.6" => [('>', '1.5'), ('<', '1.6')])
    """

    def __init__(self, line):
        # Do not call this private method
        self.line = line
        self.editable = False
        self.local_file = False
        self.specifier = False
        self.vcs = None
        self.name = None
        self.subdirectory = None
        self.uri = None
        self.path = None
        self.revision = None
        self.hash_name = None
        self.hash = None
        self.extras = []
        self.specs = []

    def __repr__(self):
        return '<Requirement: "{0}">'.format(self.line)

    def __getitem__(self, key):
        return getattr(self, key)

    def keys(self):
        return self.__dict__.keys()

    @classmethod
    def parse_editable(cls, line):
        """
        Parses a Requirement from an "editable" requirement which is either
        a local project path or a VCS project URI.
        See: pip/req.py:from_editable()
        :param line: an "editable" requirement
        :returns: a Requirement instance for the given line
        :raises: ValueError on an invalid requirement
        """

        req = cls('-e {0}'.format(line))
        req.editable = True
        vcs_match = VCS_REGEX.match(line)
        local_match = LOCAL_REGEX.match(line)

        if vcs_match is not None:
            groups = vcs_match.groupdict()
            if groups.get('login'):
                req.uri = '{scheme}://{login}@{path}'.format(**groups)
            else:
                req.uri = '{scheme}://{path}'.format(**groups)
            req.revision = groups['revision']
            if groups['fragment']:
                fragment = parse_fragment(groups['fragment'])
                egg = fragment.get('egg')
                req.name, req.extras = parse_extras_require(egg)
                req.hash_name, req.hash = get_hash_info(fragment)
                req.subdirectory = fragment.get('subdirectory')
            for vcs in VCS:
                if req.uri.startswith(vcs):
                    req.vcs = vcs
        else:
            assert local_match is not None, 'This should match everything'
            groups = local_match.groupdict()
            req.local_file = True
            if groups['fragment']:
                fragment = parse_fragment(groups['fragment'])
                egg = fragment.get('egg')
                req.name, req.extras = parse_extras_require(egg)
                req.hash_name, req.hash = get_hash_info(fragment)
                req.subdirectory = fragment.get('subdirectory')
            req.path = groups['path']

        return req

    @classmethod
    def parse_line(cls, line):
        """
        Parses a Requirement from a non-editable requirement.
        See: pip/req.py:from_line()
        :param line: a "non-editable" requirement
        :returns: a Requirement instance for the given line
        :raises: ValueError on an invalid requirement
        """

        req = cls(line)

        vcs_match = VCS_REGEX.match(line)
        uri_match = URI_REGEX.match(line)
        local_match = LOCAL_REGEX.match(line)

        if vcs_match is not None:
            groups = vcs_match.groupdict()
            if groups.get('login'):
                req.uri = '{scheme}://{login}@{path}'.format(**groups)
            else:
                req.uri = '{scheme}://{path}'.format(**groups)
            req.revision = groups['revision']
            if groups['fragment']:
                fragment = parse_fragment(groups['fragment'])
                egg = fragment.get('egg')
                req.name, req.extras = parse_extras_require(egg)
                req.hash_name, req.hash = get_hash_info(fragment)
                req.subdirectory = fragment.get('subdirectory')
            for vcs in VCS:
                if req.uri.startswith(vcs):
                    req.vcs = vcs
        elif uri_match is not None:
            groups = uri_match.groupdict()
            req.uri = '{scheme}://{path}'.format(**groups)
            if groups['fragment']:
                fragment = parse_fragment(groups['fragment'])
                egg = fragment.get('egg')
                req.name, req.extras = parse_extras_require(egg)
                req.hash_name, req.hash = get_hash_info(fragment)
                req.subdirectory = fragment.get('subdirectory')
            if groups['scheme'] == 'file':
                req.local_file = True
        elif '#egg=' in line:
            # Assume a local file match
            assert local_match is not None, 'This should match everything'
            groups = local_match.groupdict()
            req.local_file = True
            if groups['fragment']:
                fragment = parse_fragment(groups['fragment'])
                egg = fragment.get('egg')
                name, extras = parse_extras_require(egg)
                req.name = fragment.get('egg')
                req.hash_name, req.hash = get_hash_info(fragment)
                req.subdirectory = fragment.get('subdirectory')
            req.path = groups['path']
        else:
            # This is a requirement specifier.
            # Delegate to pkg_resources and hope for the best
            req.specifier = True
            pkg_req = req.parse(line)
            req.name = pkg_req.unsafe_name
            req.extras = list(pkg_req.extras)
            req.specs = pkg_req.specs
        return req

    @classmethod
    def parse(cls, line):
        """
        Parses a Requirement from a line of a requirement file.
        :param line: a line of a requirement file
        :returns: a Requirement instance for the given line
        :raises: ValueError on an invalid requirement
        """

        if line.startswith('-e') or line.startswith('--editable'):
            # Editable installs are either a local project path
            # or a VCS project URI
            return cls.parse_editable(
                re.sub(r'^(-e|--editable=?)\s*', '', line))
        return cls.parse_line(line)

def parse_pip_requirement_string(reqstr):
    """
    Parse a requirements file into a list of Requirements
    See: pip/req.py:parse_requirements()
    :param reqstr: a string or file like object containing requirements
    :returns: a *generator* of Requirement objects
    """
    filename = getattr(reqstr, 'name', None)
    try:
        # Python 2.x compatibility
        if not isinstance(reqstr, basestring):
            reqstr = reqstr.read()
    except NameError:
        # Python 3.x only
        if not isinstance(reqstr, str):
            reqstr = reqstr.read()

    for line in reqstr.splitlines():
        line = line.strip()
        if line == '':
            continue
        elif not line or line.startswith('#'):
            # comments are lines that start with # only
            continue
        elif line.startswith('-r') or line.startswith('--requirement'):
            _, new_filename = line.split()
            new_file_path = os.path.join(os.path.dirname(filename or '.'),
                                         new_filename)
            with open(new_file_path) as f:
                for requirement in parse(f):
                    yield requirement
        elif line.startswith('-f') or line.startswith('--find-links') or \
                line.startswith('-i') or line.startswith('--index-url') or \
                line.startswith('--extra-index-url') or \
                line.startswith('--no-index'):
            warnings.warn('Private repos not supported. Skipping.')
            continue
        elif line.startswith('-Z') or line.startswith('--always-unzip'):
            warnings.warn('Unused option --always-unzip. Skipping.')
            continue
        else:
            yield Requirement.parse(line)
