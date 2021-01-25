from argparse import ArgumentParser
from pathlib import Path
from time import strftime
from typing import List, Set
import re
import shutil

from lxml.etree import XML, DTD

import xml
from index import Index


def copyfile(src: Path, dst: Path) -> None:
    print(f'{src} --> {dst}')
    shutil.copyfile(src, dst)
    

def file_element(tag: str, filename: str) -> xml.Element:
    e = xml.element(tag, attrib={'file': filename})
    e.tail = '\n'
    return e


def find_images(file: Path) -> Set[str]:
    images = set()
    text = file.read_text()
    for match in re.finditer(r'src="../Images/([^"]+)"', text):
        images.add(match.group(1))
    return images


def run(ebook: Path,
        bigbook: Path,
        ubercoordinator: Path,
        files: List[Path]) -> None:
    """
    :param ebook: the ebook source directory
    :param bigbook: the Big Book of Key
    :param ubercoordinator: the ubercoordinator source directory, for the DTD
    :param files: the XHTML file from the Big Book of Key that need adding
    :return:
    """

    index = Index(bigbook)

    book_dtd = DTD((ubercoordinator / 'src' / 'book.dtd').open())
    book = xml.read(ebook / 'book.xml', dtd=book_dtd)

    illustrations = xml.get_one(book, 'illustrations')
    contents = xml.get_one(book, 'contents')

    sections = set(xml.get_all_str(contents, '//section[not(@template="yes")]/@file'))
    images = set(xml.get_all_str(illustrations, '//image/@file'))

    initial_sections = sections.copy()
    initial_images = images.copy()

    for filename in sections:
        ebook_file = ebook / 'Text' / filename
        bigbook_file = bigbook / 'Text' / filename
        if not ebook_file.exists() and bigbook_file.exists():
            copyfile(bigbook_file, ebook_file)
        if ebook_file.exists():
            for img_filename in find_images(ebook_file):
                if img_filename not in images:
                    illustrations.append(file_element('image', img_filename))
                    images.add(img_filename)
        else:
            print(f"{ebook / 'book.xml'}:0:0:WARNING: is this missing?: {filename}")

    for file in files:
        article_id = file.stem
        article = index.articles_by_id[article_id]

        if article.file.name not in sections:
            copyfile(article.file, ebook / 'Text' / article.file.name)
            title = xml.rewrap('title', XML(article.link))
            section = file_element('section', article.file.name)
            section.append(title)
            contents.append(section)
            sections.add(file.name)

        for img_filename in find_images(article.file):
            if img_filename not in images:
                illustrations.append(file_element('image', img_filename))
                images.add(img_filename)

    for img_filename in images:
        file = ebook / 'Images' / img_filename
        if not file.exists():
            copyfile(bigbook / 'Images' / img_filename, file)

    book.attrib['date'] = strftime("%Y-%m-%d")

    if sections != initial_sections or images != initial_images:
        copyfile(ebook / 'book.xml', ebook / 'book.xml.bak')
        xml.save(ebook / 'book.xml', book, doctype='book')


def main() -> None:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument(
            "-b", "--bigbook", metavar="DIR", type=Path,
            help="the Big Book of Key directory")
    parser.add_argument(
            "-e", "--ebook", metavar="DIR", type=Path,
            help="the epub directory")
    parser.add_argument(
            "-u", "--ubercoordinator", metavar="DIR", type=Path,
            help="the Ubercoordinator directory, for templates",
            default=Path(__file__).parent)
    parser.add_argument(
            "-v", "--verbose", action="store_true",
            help="print file names as they are added",
            default=False)
    parser.add_argument(
            "files", type=Path, metavar="XHTML", nargs="*",
            help="Big Book of Key files to add")
    args = parser.parse_args()
    if args.ebook and args.bigbook and args.ubercoordinator:
        run(args.ebook, args.bigbook, args.ubercoordinator, args.files)


if __name__ == "__main__":
    main()
