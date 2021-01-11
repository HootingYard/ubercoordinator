""" Some XHTML handling conveniences.
"""

from pathlib import Path
from lxml.html import tostring, HtmlElement, XHTMLParser
from lxml.etree import parse, QName, cleanup_namespaces

__all__ = ['parse_xhtml', 'xhtml_string', 'content']


def xhtml_string(element: HtmlElement) -> str:
    return tostring(element, encoding='unicode')


def parse_xhtml(file: Path) -> HtmlElement:
    """
    Parse an XHTML file into plain HTML,
    i.e. a tree of HTMLElements without namespace annotations.

    :param file: XHTML file
    :return: the 'html' element
    """
    xhtml_parser = XHTMLParser(dtd_validation=True, ns_clean=True)
    html: HtmlElement = parse(str(file), parser=xhtml_parser).getroot()
    remove_namespaces(html)
    return html


def remove_namespaces(tree: HtmlElement) -> None:
    """ Remove the namespace tags from a tree of elements """
    for element in tree.getiterator():
        element.tag = QName(element).localname
    cleanup_namespaces(tree)


def content(file: Path) -> str:
    """
    The content of an article's page, minus its heading, inside a <div> element.

    :param file: a Big Book XHTML file
    :return: the HTML as a string
    """
    html = parse_xhtml(file)
    body: HtmlElement = html.xpath('//body')[0]
    heading: HtmlElement = body.xpath('//h1')[0]
    heading.drop_tree()
    body.attrib.clear()
    body.tag = 'div'
    return tostring(body, pretty_print=True, encoding='unicode')
