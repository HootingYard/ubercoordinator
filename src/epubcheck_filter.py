# Filters Epubcheck's output into something that Emacs recognises.
# Errors in HTML files lead to the book's source directory,
# not the EPUB workspace copy.

import os
import re
import sys

BOOK = sys.argv[1]  # book source directory

HTML_ERROR_LINE = re.compile(r'''
   .* : .* / .* [.]epub/OEBPS/Text/
   (.*)
   [(] ([0-9]+) , ([0-9]+) [)]
   (.*)
''', re.VERBOSE)

XML_ERROR_LINE = re.compile(r'''
   .*: 
   (.*)
   / .* [.]epub
   / (.*)
   [(] ([0-9]+) , ([0-9]+) [)]
   (.*)
''', re.VERBOSE)

error = False

for line in sys.stdin.readlines():
    
    match = HTML_ERROR_LINE.match(line)
    if match:
        filename, line, column, message = match.group(1, 2, 3, 4)
        for directory in ['Edited', 'Text']:
            path = os.path.join(BOOK, directory, filename)
            if os.path.exists(path):
                sys.stderr.write('%s:%s:%s%s\n' % (path, line, column, message))
                error = True
                break
        continue
    
    match = XML_ERROR_LINE.match(line)
    if match:
        path1, path2, line, column, message = match.group(1, 2, 3, 4, 5)
        sys.stderr.write('%s/epub/%s:%s:%s%s\n' % (path1, path2, line, column, message))
        error = True
        continue
    
    sys.stderr.write(line)

if error:
    sys.exit(1)
