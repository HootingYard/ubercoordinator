"""
Find the data files and directories that Ubercoordinator will need.

If the environment variables BIGBOOK_DIR, WEBSITE_DIR or SHOW_INDEX_FILE
are set then those values will be used, otherwise this module
will look for repository directories inside '~/Projects/HootingYard'.
"""

__all__ = [
    'BIGBOOK_DIR',
    'WEBSITE_DIR',
    'SHOW_INDEX_FILE',
    'WEB_TEMPLATE_DIR',
]

from os import environ
from pathlib import Path
from inspect import getsourcefile


_DEFAULT_REPO_DIR = Path('~/Projects/HootingYard/').expanduser()
"""Where Glyn keeps things on his own computer."""


def _get_directory(env_variable_name: str, default_subdir: str) -> Path:
    if env_variable_name in environ:
        return Path(environ[env_variable_name]).expanduser()
    else:
        return _DEFAULT_REPO_DIR / default_subdir


def _get_ubercoordinator_dir() -> Path:
    src_dir = Path(getsourcefile(lambda _: None))  # i.e. this module's directory
    uber_dir = src_dir.parent.parent
    assert uber_dir.name == 'ubercoordinator'
    return uber_dir


BIGBOOK_DIR = _get_directory('BIG_BOOK_DIR', 'keyml/books/bigbook')
"""The Big Book of Key's base directory in the 'keyml' repository."""


SHOW_INDEX_FILE = _get_directory('SHOW_INDEX_FILE', 'analysis/index/export/export.yaml')
"""The 'export.yaml' file for the show index, from the 'analysis' repository."""


WEBSITE_DIR = _get_directory('WEBSITE_DIR', 'HootingYard.github.io')
"""The output directory for the website, in the 'HootingYard.github.io' repository."""


WEB_TEMPLATE_DIR = _get_ubercoordinator_dir() / 'templates' / 'website'
"""The directory of webpage template files."""


