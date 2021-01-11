""" Functions to arrange article entries for the indexes-by-date templates.
"""

__all__ = ['split_blogs', 'arrange_first_blog', 'month_id']

from datetime import datetime
from itertools import groupby
from typing import List, NamedTuple

from functions import sift
from index import Article, Index, year_month
from xhtml import content


def split_blogs(index: Index) -> List[List[Article]]:
    """
    Splits articles into three dictionaries, one for each
    blog Frank ran. 2003-01-01 and earlier were in the NDDirect website or
    published in pamphlets, 2003-12-01 to 2006-12-31 were the first BTOpenWorld
    blog, 2007-01-01 and later were in the second hootingyard.org blog.

    :param index: the article and show index
    :return: a list of three lists, one for each blog's list of Stories
    """

    blogs = [[], [], []]

    website_cutoff_date = datetime(2003, 1, 1)
    first_blog_cutoff_date = datetime(2006, 12, 31)

    for article in index.articles.values():
        if article.date <= website_cutoff_date:
            blogs[0].append(article)
        elif article.date <= first_blog_cutoff_date:
            blogs[1].append(article)
        else:
            blogs[2].append(article)

    return blogs


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


def month_id(date: datetime):
    return date.strftime('month-%Y-%m')
