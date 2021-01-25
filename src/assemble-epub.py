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
from typing import List
import xml
from pathlib import Path

from xml import read

BOOK = Path(sys.argv[1])
EPUB = Path(sys.argv[2])
UBER = Path(__file__).parent.parent
TEMPLATES = UBER / 'templates/epub'
OEBPS = EPUB / 'OEBPS'

assert BOOK.is_dir()
assert EPUB.is_dir()
assert UBER.is_dir()
assert OEBPS.is_dir()
assert TEMPLATES.is_dir()

book_dtd = lxml.etree.DTD(str(UBER / 'src' / 'book.dtd'))
book = xml.read(BOOK / 'book.xml', dtd=book_dtd)

error_flag = False


def error(message: str) -> None:
    global error_flag
    error_flag = True
    print(f"{BOOK / 'book.xml'}:0:0:", message, file=sys.stderr)


def expand(xsl_filepath: Path, xml_filepath: Path, doctype: str = None) -> None:
    """expand a template file using the book's book.xml metadata"""
    template = lxml.etree.XSLT(read(xsl_filepath))
    result = template(book)
    xml.save(xml_filepath, result, doctype)


def copy_files(subdirectory: str, filenames: List[str]):
    """copy files from BOOK to EPUB, using template when a file is missing"""
    for filename in filenames:
        src = BOOK / subdirectory / filename
        dst = OEBPS / subdirectory / filename
        if src.exists():
            shutil.copyfile(src, dst)
        else:
            default = TEMPLATES / subdirectory / filename
            if default.exists():
                shutil.copyfile(default, dst)
            else:
                base, ext = splitext(filename)
                template = TEMPLATES / 'XML' / (base + '.xsl')
                print(template)
                if ext in ('.html', 'xhtml') and template.exists():
                    expand(template, dst, 'xhtml')
                else:
                    error(f"{src} is missing")


def main() -> None:
    book.attrib['date'] = time.strftime("%Y-%m-%d")

    # create index files from book.xml (see .xsl files for details)
    expand(TEMPLATES / 'XML/ncx.xsl', OEBPS / 'toc.ncx')
    expand(TEMPLATES / 'XML/opf.xsl', OEBPS / 'content.opf', 'opf')

    # copy the book's files
    copy_files('Text', xml.get_all_str(book, "//section/@file"))
    copy_files('Styles', xml.get_all_str(book, "//style/@file"))
    copy_files('Images', xml.get_all_str(book, "//image/@file"))
    copy_files('Fonts', xml.get_all_str(book, "//font/@file"))

    if error_flag:
        sys.exit(1)


if __name__ == '__main__':
    main()
