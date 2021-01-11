""" Functions to arrange story entries for the indexes-by-date templates.
"""

__all__ = ['split_blogs', 'arrange_first_blog', 'month_id']

from datetime import datetime
from itertools import groupby
from typing import List, NamedTuple

from functions import sift
from index import Story, Index, year_month
from xhtml import content


def split_blogs(index: Index) -> List[List[Story]]:
    """
    Splits stories into three dictionaries, one for each
    blog Frank ran. 2003-01-01 and earlier were in the NDDirect website or
    published in pamphlets, 2003-12-01 to 2006-12-31 were the first BTOpenWorld
    blog, 2007-01-01 and later were in the second hootingyard.org blog.

    :param index: the story and show index
    :return: a list of three lists, one for each blog's list of Stories
    """

    blogs = [[], [], []]

    website_cutoff_date = datetime(2003, 1, 1)
    first_blog_cutoff_date = datetime(2006, 12, 31)

    for story in index.stories.values():
        if story.date <= website_cutoff_date:
            blogs[0].append(story)
        elif story.date <= first_blog_cutoff_date:
            blogs[1].append(story)
        else:
            blogs[2].append(story)

    return blogs


def is_intro(story: Story) -> bool:
    return story.title.startswith('Hooting Yard Archive, ')


class Day(NamedTuple):
    date: datetime
    stories: List[Story]


class Month(NamedTuple):
    date: datetime
    introduction: str  # an HTML string
    days: List[Day]


def arrange_first_blog(stories: List[Story]) -> List[Month]:
    """
    Split the first blog's stories into months and days.
    The first blog has an introduction to each month, remove that
    and extract its HTML text for use in the index.
    Most days' entries started with a quote of the day,
    move those to the starts of the days' entries.

    :param stories:
    :return: everything neatly arranged for the index page
    """
    months = []
    for (year, month), months_stories in groupby(stories, year_month):
        intro, months_stories = sift(months_stories, is_intro)
        intro = content(intro[0].file) if intro else ''
        days = []
        for date, days_stories in groupby(months_stories, lambda st: st.date):
            quotes, rest = sift(days_stories, lambda st: st.title.startswith('“'))
            days_stories = quotes + rest
            days.append(Day(date, days_stories))
        months.append(Month(datetime(year, month, 1), intro, days))
    return months


def month_id(date: datetime):
    return date.strftime('month-%Y-%m')
