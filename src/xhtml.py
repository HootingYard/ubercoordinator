""" Some XHTML handling conveniences.
"""

from pathlib import Path
from lxml.html import tostring, HtmlElement, HTMLParser
from lxml.etree import parse

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
    # xhtml_parser = XHTMLParser(dtd_validation=True, ns_clean=True)
    xhtml_parser = HTMLParser()
    html: HtmlElement = parse(str(file), parser=xhtml_parser).getroot()
    # remove_namespaces(html)
    return html


# def remove_namespaces(tree: HtmlElement) -> None:
#    """ Remove the namespace tags from a tree of elements """
#    for element in tree.getiterator():
#        element.tag = QName(element).localname
#    cleanup_namespaces(tree)


def content(file: Path, heading: bool = False) -> str:
    """
    The content of an article's page, minus its heading, inside a <div> element.
    Internal links to .xhtml files (i.e. other pages) will be replaced with '.html' links.

    :param file: a Big Book XHTML file
    :param heading: if False remove the page's first h1 element (i.e. the heading)
    :return: the HTML as a string
    """
    html = parse_xhtml(file)
    body: HtmlElement = html.xpath('//body')[0]
    if not heading:
        h1: HtmlElement = body.xpath('//h1')[0]
        h1.drop_tree()
    body.attrib.clear()
    for a in body.xpath('//a[@class="internal"]'):
        a.attrib['href'] = a.attrib['href'].replace('.xhtml', '.html')
    body.tag = 'div'
    return tostring(body, pretty_print=True, encoding='unicode')
