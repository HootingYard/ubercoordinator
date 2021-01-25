import re
from shutil import copyfile
from mako.lookup import TemplateLookup

from settings import BIGBOOK_DIR, WEBSITE_DIR, TEMPLATE_DIR, SHOW_INDEX_FILE
from index import Index


def main() -> None:
    index = Index(BIGBOOK_DIR, SHOW_INDEX_FILE)

    templates = TemplateLookup([TEMPLATE_DIR / 'website', TEMPLATE_DIR / 'website' / 'Jinja'],
                               strict_undefined=True)

    # Create website directories, if necessary.
    for dirname in ('Text', 'Images', 'Media', 'Fonts', 'Styles'):
        (WEBSITE_DIR / dirname).mkdir(exist_ok=True, parents=True)

    # Copy in the styling files from the web template.
    for dirname in ('Fonts', 'Styles', 'Images'):
        for file in (TEMPLATE_DIR / 'common' / dirname).glob('*'):
            copyfile(src=file, dst=WEBSITE_DIR / dirname / file.name)
        for file in (TEMPLATE_DIR / 'website' / dirname).glob('*'):
            copyfile(src=file, dst=WEBSITE_DIR / dirname / file.name)

    # Copy in the Big Book's media files, if necessary.
    for dirname in ('Images', 'Media'):
        for file in (BIGBOOK_DIR / dirname).glob('*'):
            dst = WEBSITE_DIR / dirname / file.name
            if not dst.exists():
                copyfile(src=file, dst=dst)

    # Expand the 'index.html' file template.
    file = TEMPLATE_DIR / 'website' / 'index.html'
    template = templates.get_template(file.name)
    html_file = WEBSITE_DIR / file.name
    html_file.write_text(template.render(index=index))

    # Expand the index pages' templates.
    for file in (TEMPLATE_DIR / 'website' / 'Text').glob('index-*.html'):
        template = templates.get_template(file.name)
        html_file = WEBSITE_DIR / 'Text' / file.name
        html_file.write_text(template.render(index=index))

    # Expand the pages for the Big Book, using the page.html template.
    for article in index.articles():
        # content = xhtml.content(article.file, heading=True)
        # I'm going to be a barbarian instead and use a regex on HTML.
        # It's acceptably accurate on these Big Book files, and much faster.
        html = article.file.read_text()
        content = re.search(r'<body[^>]*>(.+)</body>', html, re.DOTALL)[1]
        content = content.replace('.xhtml"', '.html"')
        template = templates.get_template('page.html')
        destination = WEBSITE_DIR / 'Text' / (article.id + '.html')
        destination.write_text(template.render(content=content, article=article))


if __name__ == '__main__':
    main()
