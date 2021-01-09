"""
Functions to format data into strings (mostly dates).
"""

__all__ = [
    'sexagecimal',
    'brief_date',
    'written_date',
    'full_written_date',
    'month_and_year',
    'ordinal',
    'dictionary_order_sorting_key',
]

import re
from datetime import datetime
import num2words as num2words
from unidecode import unidecode


def sexagecimal(seconds: int) -> str:
    """
    >>> sexagecimal(194)
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
    return f'{date.strftime("%B")} the {ordinal(date.day)}, {date.year}'


def full_written_date(date: datetime) -> str:
    """
    >>> full_written_date(datetime(2021, 1, 8))
    'Friday, January the 8th, 2021'
    """
    return f'{date.strftime("%A, %B")} the {ordinal(date.day)}, {date.year}'


def brief_date(date: datetime) -> str:
    """
    >>> brief_date(datetime(2012, 1, 22))
    '22nd Jan 2012'
    """
    return f'{ordinal(date.day)} {date.strftime("%b")} {date.year}'


def month_and_year(date: datetime) -> str:
    """
    >>> month_and_year(datetime(2012, 1, 22))
    'January 2012'
    """
    return date.strftime('%B %Y')


def ordinal(n: int) -> str:
    """
    >>> ordinal(3)
    '3rd'
    """
    return str(n) + {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 20, 'th')


def dictionary_order_sorting_key(title: str) -> str:
    """
    Keys for sorting titles in correct 'dictionary order':
    case is ignored;
    spaces, punctuation and accents are ignored;
    leading occurrences of "A", "An" and "The" are ignored;
    numerals are treated as if they are written as words.

    :param title: a story title
    :return: a key string representing the correct dictionary position
    """
    s = unidecode(title.casefold())
    s = s.replace("&", "and")
    s = re.sub(r"\W+", " ", s).strip()
    if s.startswith('a ') and not s.startswith('a is for '):
        s = s[2:]
    if s.startswith('an '):
        s = s[3:]
    if s.startswith('the '):
        s = s[4:]
    if s[0].isdigit():
        digits, rest = re.match(r'([0-9]+)(.*)', s).group(1, 2)
        s = num2words.num2words(int(digits)) + rest
        s = re.sub(r"\W+", " ", s)
    return s.replace(' ', '')
