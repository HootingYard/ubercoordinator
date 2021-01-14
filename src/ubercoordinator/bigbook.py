#!/usr/bin/env python3
"""
This tests that Big Book of Key XHTML files:

    (a) match a DTD, typically bigbook.dtd;

    (b) pass a set of Schematron tests, typically in bigbook.sch;

    (c) contain no broken relative links.

Optionally all linked image files can be checked for validity.
"""

# The default DTD and Schematron files should reside in the same
# directory as this script.


from sys import stderr, exit
from pathlib import Path
from argparse import ArgumentParser
from urllib.request import url2pathname
from typing import List
from inspect import getsourcefile
from PIL import Image

from lxml.isoschematron import Schematron
from lxml.html import XHTMLParser
from lxml.etree import DTD, DTDParseError, fromstring
from lxml.etree import parse, XMLSyntaxError
from lxml.etree import clear_error_log

# These are only used for type annotations:
# noinspection PyProtectedMember
from lxml.etree import _Element, _ErrorLog


__all__ = ["settings", "run"]


# XML namespaces for everything that might be used.
# (Most of these are for parsing Schematron 'svrl' errors.)
XMLNS = {
    "xhtml": "http://www.w3.org/1999/xhtml",
    "regexp": "http://exslt.org/regular-expressions",
    "xs": "http://www.w3.org/2001/XMLSchema",
    "sch": "http://purl.oclc.org/dsdl/schematron",
    "iso": "http://purl.oclc.org/dsdl/schematron",
    "svrl": "http://purl.oclc.org/dsdl/svrl",
    "schold": "http://www.ascc.net/xml/schematron",
}


class Settings:
    """
    Global settings.
    These are set by the 'argparse' command line.
    """

    dtd: Path  # path to the DTD file
    schematron: Path  # path to the Schematron file
    files: List[Path]  # XHTML files to test
    test_images: bool  # True for image file validity checks
    verbose: bool  # if True print the names of files as they are checked

    def __init__(self):
        """
        Set defaults.
        The default Schematron and DTD files are in the same
        directory as this script's source file (i.e. the one
        you ar reading now).
        """
        self.test_images = False
        self.verbose = False
        self.files = []
        data_file_dir = Path(getsourcefile(Settings)).parent
        assert data_file_dir.is_dir()
        self.dtd = data_file_dir / "bigbook.dtd"
        self.schematron = data_file_dir / "bigbook.sch"
        assert self.schematron.is_file()
        assert self.dtd.is_file()


settings = Settings()


def run(xhtml_files: List[Path]) -> bool:
    """
    Run tests on a bunch of XHTML files.
    All files are tested, even if one fails.
    Error messages are printed to stderr for files that fail.

    :param xhtml_files: the files
    :return: True if everything passes
    """
    dtd = open_dtd(settings.dtd)
    schematron = open_schematron(settings.schematron)
    success = True
    for file in xhtml_files:
        if not test(file, dtd, schematron):
            success = False
    return success


def test(xhtml_file: Path, dtd: DTD, schematron: Schematron) -> bool:
    """
    Test that an XHTML file matches a DTD and passes Schematron tests.
    Error messages are printed to stderr if the file doesn't pass.

    :param xhtml_file: the XHTML file to test
    :param dtd: the DTD
    :param schematron: the Schematron
    :return: True if the file passes
    """
    if settings.verbose:
        print(xhtml_file)

    clear_error_log()

    parser = XHTMLParser(dtd_validation=True, ns_clean=True)
    try:
        tree = parse(source=str(xhtml_file), parser=parser)
        html = tree.getroot()
    except IOError as e:
        print(f"{xhtml_file}: {e.strerror}", file=stderr)
        return False
    except XMLSyntaxError:
        print_error_log(parser.error_log)
        return False

    if not dtd.validate(html):
        print_error_log(dtd.error_log)
        return False

    if not schematron.validate(html):
        print_schematron_error_log(html, schematron)
        return False

    return test_links(xhtml_file, html) and test_images(xhtml_file, html)


def print_schematron_error_log(xhtml: _Element, schematron: Schematron) -> None:
    """
    Print a Schematron's error log in a readable format.

    :param xhtml: the root of the XHTML file with the errors
    :param schematron: the Schematron with the error log
    """
    for e in schematron.error_log:

        # The message is a XML string containing an 'srvl:failed-assert' element
        xml = fromstring(e.message)

        # Schematron reports the location of a faulty element with an Xpath selector.
        location_xpath = xml.xpath("//svrl:failed-assert/@location", namespaces=XMLNS)[
            0
        ]
        line = xhtml.xpath(location_xpath, namespaces=XMLNS)[0].sourceline

        message = xml.xpath("normalize-space(//svrl:text)", namespaces=XMLNS)

        print(f"{e.filename}:{line}:0: {message}", file=stderr)


def print_error_log(log: _ErrorLog) -> None:
    """
    Print a generic Lxml error log in a readable format.
    """
    for e in log:
        print(f"{e.filename}:{e.line}:{e.column}: {e.message}", file=stderr)


def test_images(xhtml_file: Path, xhtml: _Element) -> bool:
    """
    Test the that all 'img' links are not broken.
    If settings.test_images is True then also use PIL to
    test if the image files are valid.

    :param xhtml_file: the XHTML file's path
    :param xhtml: the XHTML files' root
    :return: True if the images are okay
    """
    success = True
    for img in xhtml.xpath("//xhtml:img", namespaces=XMLNS):
        src = str(img.attrib["src"])
        if ":" not in src:
            img_path = xhtml_file.parent / Path(url2pathname(src))

            if settings.verbose:
                print("\t", img_path)

            if not img_path.is_file():
                print(f"{xhtml_file}:1:0: missing image {img_path}", file=stderr)
                success = False
            elif settings.test_images:
                try:
                    Image.open(img_path).verify()
                except IOError:
                    print(f"{xhtml_file}:1:0: invalid image {img_path}", file=stderr)
                    success = False
    return success


def test_links(xhtml_file: Path, xhtml: _Element) -> bool:
    """
    Test the that all 'a' links to relative URLs links are not broken.

    :param xhtml_file: the XHTML file's path
    :param xhtml: the XHTML files' root
    :return: True if the links are okay
    """
    success = True
    for link in xhtml.xpath("//xhtml:a", namespaces=XMLNS):
        href = str(link.attrib["href"])
        if ":" not in href:
            path = xhtml_file.parent / Path(url2pathname(href))
            if settings.verbose:
                print("\t", path)
            if not path.exists():
                print(f"{xhtml_file}:1:0: broken relative link {path}", file=stderr)
                success = False
    return success


def open_dtd(dtd_file: Path) -> DTD:
    """
    Open a validate an XML DTD. Exit program on failure.

    :param dtd_file: path to a DTD file
    :return: A DTD object
    """
    try:
        return DTD(str(dtd_file))
    except DTDParseError as e:
        print(f"{dtd_file}:1: {e}", file=stderr)
        exit(1)


def open_schematron(schematron_file: Path) -> Schematron:
    """
    Open a Schematron schema. Exit program on failure.

    :param schematron_file: path to a Schematron XML file
    :return: A Schematron object
    """
    try:
        xml = parse(str(schematron_file))
        return Schematron(xml, store_report=True)
    except XMLSyntaxError as e:
        print(f"{schematron_file}:1: {e}", file=stderr)
        exit(1)


def main() -> None:
    """
    Go nuts with command line arguments.
    These override the defaults in 'settings'.
    """
    parser = ArgumentParser(description=__doc__)
    parser.add_argument(
        "-d", "--dtd", metavar="DTD", type=Path, help="a non-default DTD file"
    )
    parser.add_argument(
        "-x",
        "--schematron",
        metavar="SCH",
        type=Path,
        help="a non-default Schematron schema",
    )
    parser.add_argument(
        "-i", "--test-images", action="store_true", help="also test image validity"
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="print file names as they are tested",
    )
    parser.add_argument(
        "files",
        type=Path,
        metavar="XHTML",
        nargs="*",
        help="Big Book of Key files to test",
    )
    parser.parse_args(namespace=settings)

    success = run(settings.files)
    if not success:
        if settings.verbose:
            print(f"FAILURE")
        exit(1)
    elif settings.verbose:
        print(f"SUCCESS")


if __name__ == "__main__":
    main()
