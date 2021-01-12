import re
from inspect import getsourcefile
from pathlib import Path
from shutil import copyfile

from mako.lookup import TemplateLookup

from index import Index


REPO_DIR = Path('~/Projects/HootingYard/').expanduser()
WEBSITE_DIR = Path('~/Documents/HootingYard/').expanduser()
BIGBOOK_DIR = REPO_DIR / 'keyml/books/bigbook'


def template_dir() -> Path:
    """
    :return: the directory of website files and templates
    """
    src_dir = Path(getsourcefile(lambda _: None))  # i.e. this module's directory
    ubercoordinator_dir = src_dir.parent.parent
    assert ubercoordinator_dir.name == 'ubercoordinator'
    return ubercoordinator_dir / 'templates' / 'website'


def main() -> None:
    index = Index(keyml_repo=REPO_DIR/'keyml', analysis_repo=REPO_DIR/'analysis')

    templates = TemplateLookup([template_dir() / 'Text'],
                               strict_undefined=True)

    for dirname in ('Text', 'Images', 'Media', 'Fonts', 'Styles'):
        (WEBSITE_DIR / dirname).mkdir(exist_ok=True, parents=True)

    for dirname in ('Fonts', 'Styles', 'Images'):
        for file in (template_dir() / dirname).glob('*'):
            copyfile(src=file, dst=WEBSITE_DIR / dirname / file.name)

    for dirname in ('Images', 'Media'):
        for file in (BIGBOOK_DIR / dirname).glob('*'):
            dst = WEBSITE_DIR / dirname / file.name
            if not dst.exists():
                copyfile(src=file, dst=dst)

    for file in (template_dir() / 'Text').glob('index*.html'):
        template = templates.get_template(file.name)
        html_file = WEBSITE_DIR / 'Text' / file.name
        html_file.write_text(template.render(index=index))

    for article in index.articles.values():
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
