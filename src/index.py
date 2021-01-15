""" Index of the Frank Key's articles and radio shows.

This data comes from the 'bigbook/Text/toc.xhtml' file in the HootingYard 'keyml'
repository and the 'export.yaml' file in the 'archive_management' repository.
"""

__all__ = ['Narration', 'Article', 'Show', 'Index']


from dataclasses import dataclass
from itertools import groupby
from typing import Dict, List, Any, Tuple, Iterator
from pathlib import Path
from datetime import datetime

from yaml import safe_load as yaml_load
from lxml.html import HtmlElement, tostring as html_tostring

from functions import (dictionary_order_sorting_key, sift)
from files import parse_xhtml_file, read_html_content


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

    @property
    def blog(self) -> int:
        """
        Which version Frank Key's blog this article came from.
        Version 0 is the old Hooting Yard Home Page.
        """
        if self.date > datetime(2006, 12, 31):
            return 2
        elif datetime(2003, 1, 1) < self.date <= datetime(2006, 12, 31):
            return 1
        else:
            return 0

    @property
    def first_letter(self) -> str:
        """
        The first letter of the title, alphabetically. A to Z
        """
        return self.sorting_key[0].upper()


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
    :ivar articles_by_id: 'articles_by_id' is an ordered dictionary of article
    ID to Article object.
    the values are in the order that they appear in the Big Book toc.xhtml
    Sorting the values puts them into correct dictionary order.

    :ivar shows_by_id: 'shows_by_id' is an ordered dictionary of show ID to Show object.
    the values are in the order that they appear in the export.yaml

    Article and Show objects point to intermediate Narration objects that relate
    which articles were read in which shows.
    """

    articles_by_id: Dict[str, Article]  # key is id

    shows_by_id: Dict[str, Show]  # key is id

    def __init__(self, bigbook_dir: Path, show_index_file: Path) -> None:
        self.shows_by_id = {}
        self.articles_by_id = {}
        self._read_articles(bigbook_dir)
        self._read_shows(show_index_file)

    def articles(self, blog: int = -1) -> Iterator[Article]:
        if blog == -1:
            yield from self.articles_by_id.values()
        else:
            yield from filter(lambda a: a.blog == blog, self.articles_by_id.values())

    def articles_by_letter(self) -> Iterator[Tuple[str, List[Article]]]:
        yield from groupby(sorted(self.articles()), lambda a: a.first_letter)

    def articles_by_year(self, blog: int = -1) -> Iterator[Tuple[int, List[Article]]]:
        def year(a): return a.date.year
        year_sorted = sorted(self.articles(blog), key=year)
        yield from groupby(year_sorted, key=year)

    def articles_by_month(self, blog: int = -1) -> Iterator[Tuple[int, List[Article]]]:
        def year_month(a): return a.date.year, a.date.month
        year_month_sorted = sorted(self.articles(blog), key=year_month)
        for (year, month), group in groupby(year_month_sorted, key=year_month):
            yield year, month, group

    def index_for_first_blog(self) \
            -> Iterator[Tuple[datetime,
                              str,
                              List[Tuple[datetime,
                                         List[Article]]]]]:
        """
        Split the first blog's articles into groups of months containing groups of days.
        The first blog has an introduction to each month, remove that
        and extract its HTML text for use in the index.
        Most days' entries started with a quote of the day,
        move those to the starts of the days' entries.
        """
        def is_intro(article: Article) -> bool:
            return article.title.startswith('Hooting Yard Archive, ')

        for (year, month), months_articles in groupby(self.articles(1),
                                                      lambda a: (a.date.year, a.date.month)):
            intro, months_articles = sift(months_articles, is_intro)
            intro = read_html_content(intro[0].file) if intro else ''
            days = []
            for date, days_articles in groupby(months_articles, lambda a: a.date):
                quotes, rest = sift(days_articles, lambda st: st.title.startswith('“'))
                days_articles = quotes + rest
                days.append((date, days_articles))
            yield datetime(year, month, 1), intro, days

    def _read_articles(self, bigbook_dir: Path) -> None:
        text_dir = bigbook_dir / 'Text'
        toc_file = text_dir / 'toc.xhtml'
        html = parse_xhtml_file(toc_file)
        for a in html.xpath("//div[@class='contents']//a"):  # type: HtmlElement
            article = Article(a, text_dir)
            self.articles_by_id[article.id] = article

    def _read_shows(self, show_index_file: Path) -> None:
        for show_dict in yaml_load(show_index_file.open())['shows']:
            show = Show(**show_dict)
            self.shows_by_id[show.id] = show
            show.narrations = []
            for n in show_dict['narrations']:  # type: Dict[str, Any]
                article_id = n['story_id']
                if not article_id.startswith('external_'):
                    article = self.articles_by_id[article_id]
                    narration = Narration(article, show, n['start_time'],
                                          n['end_time'], n['word_count'])
                    article.narrations.append(narration)
                    show.narrations.append(narration)
            show.narrations.sort()
