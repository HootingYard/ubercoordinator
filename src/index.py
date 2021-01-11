""" Index of the Frank Key's articles and radio shows.

This data comes from the 'bigbook/Text/toc.xhtml' file in the HootingYard 'keyml'
repository and the 'export.yaml' file in the 'archive_management' repository.
"""

from dataclasses import dataclass
from typing import Dict, List, Any, Tuple
from pathlib import Path
from datetime import datetime

from yaml import safe_load as yaml_load
from lxml.html import HtmlElement, tostring as html_tostring

from functions import dictionary_order_sorting_key
from xhtml import parse_xhtml


__all__ = ['Narration', 'Article', 'Show', 'Index', 'first_letter', 'year_month']


class Article:
    """
    An story, quotation, book chapter or blog post from one of Frank's previous websites.

    :ivar id: the article ID
    :ivar title: the title, in plain Unicode ('link' contains the HTML one)
    :ivar date: date of publication
    :ivar file: Big Book of Key XHTML file
    :ivar link: an HTML 'a' element containing a link to
                the article's file and its fully formatted title
    :ivar narrations: the article's narrations in Hooting Yard on the Air
    """
    id: str
    title: str
    date: datetime
    file: Path
    link: str
    narrations: List['Narration']
    sorting_key: str

    def __init__(self, link: HtmlElement, text_dir: Path) -> None:
        """
        :param text_dir: the 'bigbook/Text' directory of article pages
        :param link: an 'a' element from the table of contents that links
                    to the article's page and contains the article's
                    fully formatted title.
        """
        self.file = text_dir / link.get('href')
        self.id = link.get('href')[:-6]  # remove ".xhtml" suffix
        self.date = datetime.fromisoformat(self.id[:10])
        self.link = html_tostring(link, encoding='unicode').replace('.xhtml', '.html')
        self.title = str(link.text_content())
        self.sorting_key = dictionary_order_sorting_key(self.title)
        self.narrations = []

    def __lt__(self, other: 'Article') -> bool:  # sorts by title
        return self.sorting_key < other.sorting_key


@dataclass
class Narration:
    """
    Frank's narration of an article on the Hooting Yard on the Air show.

    :ivar article: the article being read
    :ivar show: the show that narration is in
    :ivar start_time: roughly when the narration starts
                     (in seconds from the start of the show)
    :ivar end_time: roughly when the narration ends (i.e. when the next one starts)
    :ivar word_count: the number of words spoken (?)
    """
    article: Article
    show: 'Show'
    start_time: int
    end_time: int
    word_count: int

    def __lt__(self, other) -> bool:  # sorts by show date and start time
        if self.show.date == other.show.date:
            return self.start_time < other.start_time
        else:
            return self.show.date < other.show.date


@dataclass
class Show:
    """
    A Hooting Yard on the Air radio show

    :ivar date: date of first transmission
    :ivar title: title of the show (usually the title of the main article)
    :ivar duration: length of the show in seconds
    :ivar id: an identifier, used as the stem of audio file names
    :ivar internet_archive_url: page for the most recent upload to Archive.org
    :ivar narrations: article narrations detected within the show.
    """
    date: datetime
    title: str
    duration: int
    id: str
    internet_archive_url: str
    narrations: List[Narration]

    def __lt__(self, other) -> bool:  # sorts by date
        return self.date < other.date

    @property
    def mp3_url(self) -> str:
        url = self.internet_archive_url
        assert url.startswith('https://archive.org/details/')
        upload_name = url[url.rindex('/') + 1:]
        return f"https://archive.org/download/{upload_name}/{self.id}.mp3"


class Index:
    """
    :ivar articles: 'articles' is an ordered dictionary of article ID to Article object.
    the values are in the order that they appear in the Big Book toc.xhtml
    Sorting the values puts them into correct dictionary order.

    :ivar shows: 'shows' is an ordered dictionary of show ID to Show object.
    the values are in the order that they appear in the export.yaml

    Article and Show objects point to intermediate Narration objects that relate
    which articles were read in which shows.
    """

    articles: Dict[str, Article]  # key is id

    shows: Dict[str, Show]  # key is show_id

    def __init__(self, keyml_repo: Path, analysis_repo: Path) -> None:
        self.shows = {}
        self.articles = {}
        self._read_articles(keyml_repo)
        self._read_shows(analysis_repo)

    @property
    def sorted_articles(self) -> List[str]:
        return sorted(self.articles)

    def _read_articles(self, keyml_repo: Path) -> None:
        text_dir = keyml_repo / 'books/bigbook/Text'
        toc_file = text_dir / 'toc.xhtml'
        html = parse_xhtml(toc_file)
        print(html_tostring(html))
        for a in html.xpath("//div[@class='contents']//a"):  # type: HtmlElement
            article = Article(a, text_dir)
            self.articles[article.id] = article
            print(repr(article.id))

    def _read_shows(self, analysis: Path) -> None:
        export = analysis / 'index/export/export.yaml'
        for show_dict in yaml_load(export.open())['shows']:
            show = Show(**show_dict)
            self.shows[show.id] = show
            show.narrations = []
            for n in show_dict['narrations']:  # type: Dict[str, Any]
                article_id = n['story_id']
                if not article_id.startswith('external_'):
                    article = self.articles[article_id]
                    narration = Narration(article, show, n['start_time'],
                                          n['end_time'], n['word_count'])
                    article.narrations.append(narration)
                    show.narrations.append(narration)
            show.narrations.sort()


def first_letter(article: Article) -> str:
    """ The first letter of an article's title.

    :return: a capital letter
    """
    return article.sorting_key[0].upper()


def year_month(article: Article) -> Tuple[int, int]:
    return article.date.year, article.date.month
