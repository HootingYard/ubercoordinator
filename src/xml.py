""" etree XML conveniences """

__all__ = [
    'Element',
    'element',
    'read',
    'save',
    'get_one',
    'get_all',
    'get_all_str',
    'rewrap',
    'NoMatch',
]

# noinspection PyProtectedMember
from copy import deepcopy

from lxml.etree import _Element as Element  # only used as a type
from lxml.etree import DTD, XMLParser, parse, tostring, Element as element
from pathlib import Path
from typing import List

BOOK_DOCTYPE = '''<?xml version="1.0"?>
<!DOCTYPE book SYSTEM "book.dtd">'''

NCX_DOCTYPE = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE ncx PUBLIC "-//NISO//DTD ncx 2005-1//EN" 
    "http://www.daisy.org/z3986/2005/ncx-2005-1.dtd">'''

OPF_DOCTYPE = '<?xml version="1.0"?>\n'

XHTML_DOCTYPE = '''<?xml version="1.0" encoding="utf-8" standalone="no"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"
  "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">'''

doctypes = {
    None: None,
    'book': BOOK_DOCTYPE,
    'ncx': NCX_DOCTYPE,
    'opf': OPF_DOCTYPE,
    'html': XHTML_DOCTYPE,
    'xhtml': XHTML_DOCTYPE,
}

namespaces = {
    'book': 'book.dtd',
    'ncx': 'http://www.daisy.org/z3986/2005/ncx/',
    'opf': 'http://www.idpf.org/2007/opf',
    'dc': "http://purl.org/dc/elements/1.1/",
    'html': "http://www.w3.org/1999/xhtml",
    'xhtml': "http://www.w3.org/1999/xhtml",
    're': "http://exslt.org/regular-expressions",
}


def read(filepath: Path, dtd: DTD = None) -> Element:
    with filepath.open(encoding='utf-8') as f:
        root = parse(f, XMLParser()).getroot()
    if dtd:
        dtd.validate(root)
    return root


def save(filepath: Path, document: Element, doctype: str = None) -> None:
    s = tostring(document,
                 doctype=doctypes[doctype],
                 encoding='unicode',
                 pretty_print=True)
    s = s.replace(u'/><', u'/>\n<').replace(u' xmlns=""', u'')
    filepath.write_bytes(s.encode('utf-8'))


class NoMatch(ValueError):
    pass


def get_one(element: Element, xpath: str) -> Element:
    """get the unique XML subelement that matches xpath"""
    xs = element.xpath(xpath + '[1]', namespaces=namespaces)
    if len(xs) == 1 and isinstance(xs[0], Element):
        return xs[0]
    else:
        raise NoMatch(xpath)


def get_all(element: Element, xpath: str) -> List[Element]:
    """get the list of XML subelements that match xpath"""
    xs = element.xpath(xpath, namespaces=namespaces)
    for x in xs:
        if not isinstance(x, Element):
            raise NoMatch(xpath)
    return xs


def get_all_str(element: Element, xpath: str) -> List[str]:
    """get the list of attribute or text strings that match xpath"""
    for x in element.xpath(xpath, namespaces=namespaces):
        yield str(x)


def rewrap(tag: str, source: Element) -> Element:
    """copy all the contents of one element into another"""
    new = element(tag)
    new.text = source.text
    for e in source.getchildren():
        new.append(deepcopy(e))
    return new
