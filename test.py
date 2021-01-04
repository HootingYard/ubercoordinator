""" Give index.py a little tryout.
"""

from pathlib import Path
from index import Index, Story
from itertools import groupby


REPO_DIR = Path('~/Projects/HootingYard/').expanduser()


def year_month(story: Story) -> str:
    return story.date.strftime('%B %Y')  # "January 2013"


def main() -> None:
    index = Index(keyml_repo=REPO_DIR/'keyml', analysis_repo=REPO_DIR/'analysis')
    for date_str, group in groupby(index.stories.values(), year_month):
        print()
        print('=' * 80)
        print(date_str)
        print('=' * 80)
        for story in group:  # type: Story
            print(story.title)
            for narration in story.narrations:
                show = narration.show
                print('\t', show.date.isoformat(), show.internet_archive_url)


if __name__ == '__main__':
    main()
