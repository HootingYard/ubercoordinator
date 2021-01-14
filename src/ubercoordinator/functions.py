"""
Handy miscellaneous functions.
"""

__all__ = ["sift", "dictionary_order_sorting_key"]

import re
from typing import List, TypeVar, Tuple, Callable, Iterable
from num2words import num2words
from unidecode import unidecode

A = TypeVar("A")


def sift(
    sequence: Iterable[A], condition: Callable[[A], bool]
) -> Tuple[List[A], List[A]]:
    """
    Sift an iterable into two lists: one for elements that match a condition
    and one for elements that do not.
    :param sequence: the iterable
    :param condition: the condition
    :return: thw two lists, matching list first
    """
    gold = []
    dross = []
    for element in sequence:
        if condition(element):
            gold.append(element)
        else:
            dross.append(element)
    return gold, dross


def dictionary_order_sorting_key(title: str) -> str:
    """
    Keys for sorting titles in correct 'dictionary order':
    case is ignored;
    spaces, punctuation and accents are ignored;
    leading occurrences of "A", "An" and "The" are ignored;
    numerals are treated as if they are written as words.

    :param title: an article title
    :return: a key string representing the correct dictionary position
    """
    s = unidecode(title.casefold())
    s = s.replace("&", "and")
    s = re.sub(r"\W+", " ", s).strip()
    if s.startswith("a ") and not s.startswith("a is for "):
        s = s[2:]
    if s.startswith("an "):
        s = s[3:]
    if s.startswith("the "):
        s = s[4:]
    if s[0].isdigit():
        digits, rest = re.match(r"([0-9]+)(.*)", s).group(1, 2)
        s = num2words(int(digits)) + rest
        s = re.sub(r"\W+", " ", s)
    return s.replace(" ", "")
