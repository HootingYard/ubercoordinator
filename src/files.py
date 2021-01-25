
__all__ = [
    'parse_xhtml_file',
    'read_html_content',
]

from pathlib import Path
from lxml.etree import parse
from lxml.html import HtmlElement, HTMLParser, tostring


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


r'''
class Finder:
    """
    Search for a file in a sequence of directories,
    and if that fails the try to find a suitable template file.
    """
    def __init__(self, *paths: Path, templates: Path = None) -> None:
        self.paths = paths
        self.templates = templates

    def __call__(self, subdir: str, filename: str) -> Path:
        for directory in self.paths:
            path = directory / subdir / filename
            if path.exists():
                return path
        if self.templates:
            stem, _ = splitext(filename)
            for file in self.templates.glob('*'):
                if file.stem == stem:
                    return file
        raise FileNotFoundError(filename)
'''