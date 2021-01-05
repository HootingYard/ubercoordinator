""" Index of the Frank Key's stories and radio shows.

This data comes from the 'bigbook/Text/toc.xhtml' file in the HootingYard 'keyml'
repository and the 'export.yaml' file in the 'archive_management' repository.
"""
import re
import collections
from copy import deepcopy
from dataclasses import dataclass
from typing import Set, OrderedDict, Dict, List, Any
from pathlib import Path
from datetime import datetime
from unidecode import unidecode
from yaml import safe_load
from lxml.html import HtmlElement

from xhtml import parse_xhtml


__all__ = ['Narration', 'Story', 'Show', 'Index']


@dataclass
class Story0:
    id: str
    title: str
    date: datetime
    file: Path
    title_link: HtmlElement
    narrations: Set['Narration']
    sorting_key: str

    def __lt__(self, other: 'Story') -> bool:  # sorts by title
        return self.sorting_key < other.sorting_key


@dataclass(eq=False)
class Narration:
    story: Story
    show: 'Show'
    start_time: int
    end_time: int
    word_count: int


@dataclass(eq=False)
class Show:
    date: datetime
    title: str
    duration: int
    id: str
    internet_archive_url: str
    narrations: List[Narration]

    def __lt__(self, other: 'Story') -> bool:  # sorts by date
        return self.date < other.date

    @property
    def mp3_url(self) -> str:
        url = self.internet_archive_url
        assert url.startswith('https://archive.org/details/')
        upload_name = url[url.rindex('/') + 1:]
        return f"https://archive.org/download/{upload_name}/{self.id}.mp3"


class Index:
    """
    :ivar stories: an ordered dictionary of story ID to Story object.
    the values are in the order that they appear in the Big Book toc.xhtml
    Sorting the values puts them into correct dictionary order.

    :ivar shows: an ordered dictionary of show ID to Show object.
    the values are in the order that they appear in the export.yaml

    Story and Show point to intermediate Narration objects that relate
    which stories were read in which shows and when.
    """
    stories: OrderedDict[str, Story]  # key is story_id
    shows: OrderedDict[str, Show]   # key is show_id

    def __init__(self, keyml_repo: Path, analysis_repo: Path) -> None:
        self.shows = collections.OrderedDict()
        self.stories = collections.OrderedDict()
        self._read_stories(keyml_repo)
        self._read_shows(analysis_repo)

    def _read_stories(self, keyml_repo: Path) -> None:
        text_dir = keyml_repo / 'books/bigbook/Text'
        toc_file = text_dir / 'toc.xhtml'
        html = parse_xhtml(toc_file)
        for p in html.xpath('//p'):  # type: HtmlElement
            filename = str(p.xpath('a/@href')[0])
            file = text_dir / filename
            story_id = filename[:-6]  # remove ".xhtml" suffix
            date = datetime.fromisoformat(p.text[:10])
            title_link = deepcopy(p.xpath('a')[0])
            title = str(title_link.text_content())
            sorting_key = dictionary_order_sorting_key(title)
            self.stories[story_id] = \
                Story(story_id, title, date, file, title_link, set(), sorting_key)

    def _read_shows(self, analysis: Path) -> None:
        export = analysis / 'index/export/export.yaml'
        with export.open() as fp:
            yaml: List[Dict[str, Any]] = safe_load(fp)['shows']
        for show_dict in yaml:
            show = Show(**show_dict)
            self.shows[show.id] = show
            show.narrations = []
            for n in show_dict['narrations']:  # type: Dict[str, Any]
                story_id = n['story_id']
                if not story_id.startswith('external_'):
                    story = self.stories[story_id]
                    narration = Narration(story, show, n['start_time'],
                                          n['end_time'], n['word_count'])
                    story.narrations.add(narration)
                    show.narrations.append(narration)


def dictionary_order_sorting_key(title: str) -> str:
    """
    Keys for sorting titles in correct dictionary order.
    I.e. case, accents, spaces, punctuation and leading occurrences
    of "A", "An" and "The" are all to be ignored when sorting.

    :param title: a story title
    :return: a key string representing the correct dictionary position
    """
    s = unidecode(title.casefold())
    s = s.replace("&", "and")
    s = re.sub(r"\W+", " ", s).strip()
    if s.startswith('a ') and not s.startswith('a is for '):
        s = s[2:] + ' a'
    if s.startswith('an '):
        s = s[3:] + ' an'
    if s.startswith('the '):
        s = s[4:] + ' the'
    return s.replace(' ', '')
