""" Copy the files listed in a book's book.xml,
    and create EPUB index files from the metadata in book.xml.
    Default files and XSLT style sheets from the code directory
    are used to supply files missing from the book directory.
"""

import shutil
import sys
import time
from os.path import splitext

import lxml.etree
from typing import List, Optional
import xml
from pathlib import Path

from xml import read

BOOK = Path(sys.argv[1])
EPUB = Path(sys.argv[2])
CODE = Path(__file__).parent

OEBPS = EPUB / 'OEBPS'
DEFAULTS = [CODE / 'templates' / 'epub', CODE / 'templates' / 'common']
TEMPLATES = CODE / 'templates' / 'epub' / 'XML'

book_dtd = lxml.etree.DTD(str(CODE / 'book.dtd'))

book = xml.read(BOOK / 'book.xml', dtd=book_dtd)
book.attrib['date'] = time.strftime("%Y-%m-%d")


def expand(xsl_filepath: Path,
           xml_filepath: Path,
           doctype: Optional[str] = None):
    """expand a template file using the book's book.xml metadata"""
    template = lxml.etree.XSLT(read(xsl_filepath))
    result = template(book)
    xml.save(xml_filepath, result, doctype)


def copy_files(subdirectory: str, filenames: List[str]) -> None:
    """
    copy files from BOOK to EPUB, using a default or template
    when a file is missing
    """
    for filename in filenames:
        src = BOOK / subdirectory / filename
        dst = OEBPS / subdirectory / filename
        if src.exists():
            shutil.copyfile(str(src), str(dst))
            return

        for default_dir in DEFAULTS:
            default = default_dir / subdirectory / filename
            if default.exists():
                shutil.copyfile(str(default), str(dst))
            return

        base, ext = splitext(filename)
        xsl_filepath = TEMPLATES / (base + '.xsl')
        if ext == '.xhtml' and xsl_filepath.exists():
            expand(xsl_filepath, dst, doctype='xhtml')
            return

        raise IOError(f'No file for {subdirectory}/{filename}')


# copy in EPUB identification files
(EPUB / 'META-INF').mkdir(parents=True, exist_ok=True)
shutil.copyfile(TEMPLATES / 'xml/mimetype',
                EPUB / 'mimetype')
shutil.copy(TEMPLATES / 'xml/container.xml',
            EPUB / 'META-INF' / 'container.xml')


# create index files from book.xml (see .xsl files for details)
expand(TEMPLATES / 'ncx.xsl', OEBPS / 'toc.ncx', doctype=None)
expand(TEMPLATES / 'opf.xsl', OEBPS / 'content.opf', doctype='opf')


# copy the book's files
copy_files('Text', xml.get_all_str(book, "//section/@file"))
copy_files('Images', xml.get_all_str(book, "//image/@file"))
copy_files('Fonts', xml.get_all_str(book, "//font/@file"))
copy_files('Styles', xml.get_all_str(book, "//style/@file"))
