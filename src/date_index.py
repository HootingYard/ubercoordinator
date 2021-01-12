""" Functions to arrange article entries for the indexes-by-date templates.
"""

__all__ = [
    'from_web_page',
    'from_first_blog',
    'from_second_blog',
    'arrange_first_blog',
    'month_id',
    'date_back_link',
    'title_back_link',
]

from datetime import datetime
from itertools import groupby
from typing import List, NamedTuple

from functions import sift
from index import Article, year_month
from xhtml import content


website_cutoff_date = datetime(2003, 1, 1)
first_blog_cutoff_date = datetime(2006, 12, 31)


def from_web_page(article: Article) -> bool:
    """
    True if this article belonged in the 'Hooting Yard Web Page' site.
    2003-01-01 and earlier were in the NDDirect website or
    published in pamphlets.
    """
    return article.date <= website_cutoff_date


def from_first_blog(article: Article) -> bool:
    """
    True if this article belonged in the first blog, the 'Hooting Yard Blog'.
    2003-12-01 to 2006-12-31 were the first BTOpenWorld blog.
    """
    return website_cutoff_date < article.date <= first_blog_cutoff_date


def from_second_blog(article: Article) -> bool:
    """
    True if this article belonged in the second blog, 'Hooting Yard'.
    2007-01-01 and later were in the second hootingyard.org blog.
    """
    return article.date > first_blog_cutoff_date


def date_back_link(article: Article) -> str:
    if from_web_page(article):
        return 'index-by-date-1992-2003.html#' + article.id
    elif from_first_blog(article):
        return 'index-by-date-2003-2006.html#' + article.id
    else:
        return 'index-by-date-2006-2019.html#' + article.id


def title_back_link(article: Article) -> str:
    return 'index-by-title.html#' + article.id


def is_intro(article: Article) -> bool:
    return article.title.startswith('Hooting Yard Archive, ')


class Day(NamedTuple):
    date: datetime
    articles: List[Article]


class Month(NamedTuple):
    date: datetime
    introduction: str  # an HTML string
    days: List[Day]


def arrange_first_blog(articles: List[Article]) -> List[Month]:
    """
    Split the first blog's articles into months and days.
    The first blog has an introduction to each month, remove that
    and extract its HTML text for use in the index.
    Most days' entries started with a quote of the day,
    move those to the starts of the days' entries.

    :param articles:
    :return: everything neatly arranged for the index page
    """
    months = []
    for (year, month), months_articles in groupby(articles, year_month):
        intro, months_articles = sift(months_articles, is_intro)
        intro = content(intro[0].file) if intro else ''
        days = []
        for date, days_articles in groupby(months_articles, lambda st: st.date):
            quotes, rest = sift(days_articles, lambda st: st.title.startswith('“'))
            days_articles = quotes + rest
            days.append(Day(date, days_articles))
        months.append(Month(datetime(year, month, 1), intro, days))
    return months


def month_id(date: datetime) -> str:
    return date.strftime('month-%Y-%m')
