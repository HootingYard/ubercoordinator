"""
Handy miscellaneous functions.
"""

__all__ = [
    'parse_xhtml_file',
    'read_html_content',
    'sift',
    'dictionary_order_sorting_key'
]

import re
from typing import List, TypeVar, Tuple, Callable, Iterable
from pathlib import Path
from lxml.html import tostring, HtmlElement, HTMLParser
from lxml.etree import parse
import num2words as num2words
from unidecode import unidecode


A = TypeVar('A')


def sift(sequence: Iterable[A],
         condition: Callable[[A], bool]) -> Tuple[List[A], List[A]]:
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


def parse_xhtml_file(file: Path) -> HtmlElement:
    """
    Parse an XHTML file into plain HTML,
    i.e. a tree of HTMLElements without namespace annotations.

    :param file: XHTML file
    :return: the 'html' element
    """
    # The HTMLParser seems to do what I want okay...
    return parse(str(file), parser=HTMLParser()).getroot()


def read_html_content(file: Path, heading: bool = False) -> str:
    """
    The content of an article's page, minus its heading, inside a <div> element.
    Internal links to .xhtml files (i.e. other pages) will be replaced with '.html' links.

    :param file: a Big Book XHTML file
    :param heading: if False remove the page's first h1 element (i.e. the heading)
    :return: the HTML as a string
    """
    html = parse_xhtml_file(file)
    body: HtmlElement = html.xpath('//body')[0]
    if not heading:
        h1: HtmlElement = body.xpath('//h1')[0]
        h1.drop_tree()
    body.attrib.clear()
    for a in body.xpath('//a[@class="internal"]'):
        a.attrib['href'] = a.attrib['href'].replace('.xhtml', '.html')
    body.tag = 'div'
    return tostring(body, pretty_print=True, encoding='unicode')
