# Makefile.inc --- rules to be included into Makefiles -*-Makefile-*-

# These variables must be defined by the including Makefile:
#
# NAME      = filename for the book (with no extension)
# BOOK      = directory of book's data
# UBER      = directory of scripts and templates
# WORKSPACE = working directory
# OUTPUT    = directory for ebook output
#
# OUTPUT and WORKSPACE must be writable.

CODE=$(UBER)/src
TEMPLATES=$(UBER)/templates/epub

# The Makefile targets:

.phony :: default epub clean

default : epub

epub   : $(OUTPUT)/$(NAME).epub
kindle : $(OUTPUT)/$(NAME).mobi

# workspace for building ebook

WORK=$(WORKSPACE)/$(NAME)

# book source files

SOURCE = \
    $(BOOK)/book.xml \
    $(BOOK)/cover.png \
    $(wildcard $(BOOK)/Text/*.html) \
    $(wildcard $(BOOK)/Edits/*.html) \
    $(wildcard $(BOOK)/Styles/*.css) \
    $(wildcard $(BOOK)/Fonts/*.ttf) \
    $(wildcard $(BOOK)/Images/*.jpg) \
    $(wildcard $(BOOK)/Images/*.gif) \
    $(wildcard $(BOOK)/Images/*.png) \

# default book items 

DEFAULTS = \
    $(wildcard $(TEMPLATES)/Text/*.html) \
    $(wildcard $(TEMPLATES)/Styles/*.css) \
    $(wildcard $(TEMPLATES)/Fonts/*.ttf) \
    $(wildcard $(TEMPLATES)/Images/*.jpg) \
    $(wildcard $(TEMPLATES)/Images/*.gif) \
    $(wildcard $(TEMPLATES)/Images/*.png)

# scripts for building EPUBs

SCRIPTS = \
    $(CODE)/assemble-epub.py \
    $(CODE)/xml.py \
    $(CODE)/Makefile.inc \
    $(CODE)/clean-epub.sh \
    $(CODE)/book.dtd \
    $(wildcard $(TEMPLATES)/XML/*.xsl)

# Make EPUB

EPUB=$(WORK)/epub

$(WORK)/book.epub : $(SOURCE) $(DEFAULTS) $(SCRIPTS)
	sh $(CODE)/clean-epub.sh $(EPUB) $(TEMPLATES)
	python3 $(CODE)/assemble-epub.py $(BOOK) $(EPUB)
	cd $(EPUB) ; \
	zip -0Xqv --quiet $(abspath $(WORK))/book.epub mimetype && \
	zip -Xr9Dqv --quiet $(abspath $(WORK))/book.epub META-INF OEBPS
	epubcheck $(WORK)/book.epub 2>&1 | python3 $(CODE)/epubcheck_filter.py $(BOOK)

$(OUTPUT)/$(NAME).epub : $(WORK)/book.epub
	mkdir -p $(OUTPUT)
	cp $(WORK)/book.epub $(OUTPUT)/$(NAME).epub

# Clean

clean :
	sh $(CODE)/clean-epub.sh $(EPUB) $(TEMPLATES)
	rm -f $(WORK)/book.epub
	rm -f $(WORK)/book.mobi

#end
