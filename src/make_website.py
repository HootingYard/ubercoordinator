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
    return ubercoordinator_dir / 'website' / 'templates'


def main() -> None:
    index = Index(keyml_repo=REPO_DIR/'keyml', analysis_repo=REPO_DIR/'analysis')

    templates = TemplateLookup([template_dir() / 'Text'],
                               strict_undefined=True)

    for dirname in ('Text', 'Images', 'Media', 'Fonts', 'Styles'):
        (WEBSITE_DIR / dirname).mkdir(exist_ok=True, parents=True)

    for dirname in ('Fonts', 'Styles', 'Images'):
        for file in (template_dir() / dirname).glob('*'):
            copyfile(src=file, dst=WEBSITE_DIR / dirname / file.name)

    for file in (BIGBOOK_DIR / 'Images').glob('*'):
        dst = WEBSITE_DIR / 'Images' / file.name
        if not dst.exists():
            copyfile(src=file, dst=dst)

    for file in (template_dir() / 'Text').glob('index*.html'):
        template = templates.get_template(file.name)
        html_file = WEBSITE_DIR / 'Text' / file.name
        html_file.write_text(template.render(index=index))

    for story in index.stories.values():
        # I'm going to be a barbarian and use a regex on HTML...
        html = story.file.read_text()
        content = re.search(r'<body[^>]*>(.+)</body>', html, re.DOTALL)[1]
        template = templates.get_template('page.html')
        destination = WEBSITE_DIR / 'Text' / (story.story_id + '.html')
        destination.write_text(template.render(content=content, story=story))


if __name__ == '__main__':
    main()
