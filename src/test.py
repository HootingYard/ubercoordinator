""" Give index.py a little tryout. """

from pathlib import Path
from index import Index, Story

REPO_DIR = Path('~/Projects/HootingYard/').expanduser()


def main() -> None:
    index = Index(keyml_repo=REPO_DIR/'keyml', analysis_repo=REPO_DIR/'analysis')
    for story in index.stories.values():  # type: Story
        pass


if __name__ == '__main__':
    main()
