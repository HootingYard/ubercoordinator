""" Some XHTML handling conveniences.
"""

from copy import deepcopy
from pathlib import Path

from lxml.html import HtmlElement, XHTMLParser
from lxml.etree import parse, QName, cleanup_namespaces

__all__ = ['parse_xhtml', 'as_h1_element']


def parse_xhtml(file: Path) -> HtmlElement:
    """
    Parse an XHTML file into plain HTML.

    :param file: XHTML file
    :return: HTML head element, with no namespaces
    """
    parser = XHTMLParser(dtd_validation=True, ns_clean=True)
    html: HtmlElement = parse(str(file), parser=parser).getroot()
    remove_namespaces(html)
    return html


def remove_namespaces(tree: HtmlElement) -> None:
    """ Remove the namespace tags from a tree of elements """
    for element in tree.getiterator():
        element.tag = QName(element).localname
    cleanup_namespaces(tree)


def as_h1_element(element: HtmlElement) -> HtmlElement:
    """
    Convert any element into an 'h1' header.
    Only the 'em' tags in the element will be preserved.

    :param element: the element
    :return: the h1 element
    """
    h1 = deepcopy(element)
    h1.attrib.clear()
    h1.tag = 'h1'
    for element in h1.getiterator():  # type: HtmlElement
        if element.tag not in ('em', 'h1'):
            element.drop_tag()
    return h1
