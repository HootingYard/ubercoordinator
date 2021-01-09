from inspect import getsourcefile
from pathlib import Path
from shutil import copyfile

from mako.lookup import TemplateLookup

from index import Index


REPO_DIR = Path('~/Projects/HootingYard/').expanduser()
WEBSITE_DIR = Path('~/Documents/HootingYard/').expanduser()


def template_dir() -> Path:
    src_dir = Path(getsourcefile(lambda _: None))
    ubercoordinator = src_dir.parent.parent
    assert ubercoordinator.name == 'ubercoordinator'
    return ubercoordinator / 'website' / 'templates' / 'Text'


def main() -> None:
    index = Index(keyml_repo=REPO_DIR/'keyml', analysis_repo=REPO_DIR/'analysis')

    templates = TemplateLookup([template_dir()],
                               module_directory='/tmp/mako_modules',
                               output_encoding='utf-8',
                               strict_undefined=True)

    for dirname in ('Text', 'Images', 'Media', 'Fonts', 'Styles'):
        (WEBSITE_DIR / dirname).mkdir(exist_ok=True, parents=True)

    for dirname in ('Fonts', 'Styles'):
        for file in (template_dir() / dirname).glob('*'):
            copyfile(file, WEBSITE_DIR / dirname / file.name)

    # for filename in ('index_by_title.html', 'index_by_date.html'):
    for filename in ('index_by_title.html',):
        template = templates.get_template(filename)
        html_file = WEBSITE_DIR / 'Text' / filename
        html_file.write_bytes(template.render(index=index))


if __name__ == '__main__':
    main()
