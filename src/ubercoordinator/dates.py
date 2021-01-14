"""
Functions to format dates into strings.
"""

__all__ = [
    "minute_second",
    "brief_date",
    "written_date",
    "full_written_date",
    "month_and_year",
    "month_id",
]

from datetime import datetime


def minute_second(seconds: int) -> str:
    """
    >>> minute_second(194)
    '03:14'
    """
    m = seconds // 60
    s = seconds % 60
    return f"{m:02}:{s:02}"


def written_date(date: datetime) -> str:
    """
    >>> written_date(datetime(2012, 1, 22))
    'January the 22nd, 2012'
    """
    return f'{date.strftime("%B")}&nbsp;the&nbsp;{ordinal(date.day)},&nbsp;{date.year}'


def full_written_date(date: datetime) -> str:
    """
    >>> full_written_date(datetime(2021, 1, 8))
    'Friday, January the 8th, 2021'
    """
    return f'{date.strftime("%A,&nbsp;%B")}&nbsp;the&nbsp;{ordinal(date.day)},&nbsp;{date.year}'


def brief_date(date: datetime) -> str:
    """
    >>> brief_date(datetime(2012, 1, 22))
    '22nd Jan 2012'
    """
    return f'{ordinal(date.day)}&nbsp;{date.strftime("%b")}&nbsp;{date.year}'


def month_and_year(date: datetime) -> str:
    """
    >>> month_and_year(datetime(2012, 1, 22))
    'January 2012'
    """
    return date.strftime("%B&nbsp;%Y")


def ordinal(n: int) -> str:
    """
    >>> ordinal(3)
    '3rd'
    """
    return str(n) + {1: "st", 2: "nd", 3: "rd"}.get(n % 20, "th")


def month_id(date: datetime) -> str:
    return date.strftime("month-%Y-%m")
