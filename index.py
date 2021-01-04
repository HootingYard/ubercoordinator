""" Index of the Frank Key's stories and radio shows.

This data comes from the 'bigbook/Text/toc.xhtml' file in the HootingYard 'keyml'
repository and the 'export.yaml' file in the 'archive_management' repository.
"""

from dataclasses import dataclass
from typing import Set, OrderedDict, Dict, List, Any
from pathlib import Path
from datetime import datetime
from yaml import safe_load
from lxml.html import HtmlElement
import collections

from xhtml import as_h1_element, parse_xhtml


__all__ = ['Narration', 'Story', 'Show', 'Index']


@dataclass(eq=False)
class Story:
    id: str
    title: str
    date: datetime
    file: Path
    header: HtmlElement
    narrations: Set['Narration']


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


class Index:
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
            header = as_h1_element(p.xpath('a')[0])
            title = str(header.text_content())
            self.stories[story_id] = Story(story_id, title, date, file, header, set())

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
                    narration = Narration(story,
                                          show,
                                          n['start_time'],
                                          n['end_time'],
                                          n['word_count'])
                    story.narrations.add(narration)
                    show.narrations.append(narration)

