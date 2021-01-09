""" Give index.py a little tryout. """

from html import escape
from pathlib import Path
from itertools import groupby

from xhtml import xhtml_string

from formatting import sexagecimal, written_date, month_and_year
from index import Index, Story, Narration


REPO_DIR = Path('~/Projects/HootingYard/').expanduser()


def main() -> None:
    index = Index(keyml_repo=REPO_DIR/'keyml', analysis_repo=REPO_DIR/'analysis')
    # dump_narration_list(index)
    index_file = REPO_DIR / 'keyml/books/bigbook/Text/index_by_title.html'
    index_file.write_text(index_by_title(index))
    # print_titles_and_narrations_by_month(index)


def dump_narration_list(index: Index) -> None:
    for date_str, group in groupby(index.stories.values(), month_and_year):
        for story in group:  # type: Story
            print(story.title)
            for narration in story.narrations:
                print('\t', narration.show.date, narration.start_time)
                print('\t', narration.show.mp3_url)


def print_titles_and_narrations_by_month(index) -> None:
    for date_str, group in groupby(index.stories.values(), month_and_year):
        for story in group:  # type: Story
            if 'Tosspot' not in story.title:
                continue
            if story.narrations:
                print(audio_footer(story))


def audio_footer(story: Story) -> str:
    audio_players = ''.join(map(audio_player, sorted(story.narrations)))
    return AUDIO_FOOTER.format(audio_players=audio_players)


def audio_player(narration: Narration) -> str:
    show = narration.show
    return AUDIO_PLAYER.format(
        title=escape(show.title),
        url=show.internet_archive_url,
        date=written_date(show.date),
        mp3=show.mp3_url,
        file=show.mp3_url[show.mp3_url.rindex('/') + 1:],
        time=sexagecimal(narration.start_time))


AUDIO_FOOTER = r'''<div id="audio">{audio_players}</div>'''


AUDIO_PLAYER = r'''
<div class="player">
    <p>Hooting Yard on the Air, 
        <a href="{url}" title="View on the Internet Archive">{date}</a>&nbsp;: 
        “{title}” (starts&nbsp;at&nbsp;{time})</a>
    </p>
    <audio controls src="{mp3}">
        <p>Download: <a href="{mp3}">{file}</a></p>
    </audio>
</div>
'''


ALPHABETICAL_INDEX = r'''<!DOCTYPE html>
<html>
<head>
  <title>Hooting Yard Index</title>
  <meta name="author" content="Hooting Yard Archivists (a.k.a. The Soup Committee)" />
  <meta name="description" content="An alphabetical index of the works by Frank Key." />
  <meta name="language" content="en-GB" />
  <meta name="generator" content="ÜBERCOÖDINATOR" />
  <meta http-equiv="content-type" content="text/html; charset=utf-8" />
  <link href="../Styles/style.css" rel="stylesheet" type="text/css" />
</head>
<body class="toc">
<h1>The Unhelpful Index</h1>

    <p><em>This index lists the headings of all the items on the main pages 
    of Hooting Yard, together with the relevant date. <em>[…]</em> 
    frankly, it has a beauty of its own simply as a list. 
    Hint&nbsp;: next time you are buttonholed by someone demanding to 
    know why Hooting Yard is a bright and glistening jewel in 
    a wasteland of twaddle, just send them this page.</em> —Frank Key</p>

<div class="contents">
<h2>
<a href="#A">A</a>
<a href="#B">B</a>
<a href="#C">C</a>
<a href="#D">D</a>
<a href="#E">E</a>
<a href="#F">F</a>
<a href="#G">G</a>
<a href="#H">H</a>
<a href="#I">I</a>
<a href="#J">J</a>
<a href="#K">K</a>
<a href="#L">L</a>
<a href="#M">M</a>
<a href="#N">N</a>
<a href="#O">O</a>
<a href="#P">P</a>
<a href="#Q">Q</a>
<a href="#R">R</a>
<a href="#S">S</a>
<a href="#T">T</a>
<a href="#U">U</a>
<a href="#V">V</a>
<a href="#W">W</a>
<a href="#X">X</a>
<a href="#Y">Y</a>
<a href="#Z">Z</a>
</h2>
{groups}
</div>
</body>
</html>
'''

ALPHABETICAL_GROUP = r'''
    <div id="{letter}">
        <h2>{letter} is for…</h2>
        <div>
        {entries}
        </div
    </div>
'''

ALPHABETICAL_ITEM = r'''<p>{link} <em>— {date}</em></p>
'''


def alphabetical_item(story: Story) -> str:
    date = written_date(story.date)
    link = story.link
    if story.title.startswith('“'):
        link = f'<em>{story.link}</em>'
    return ALPHABETICAL_ITEM.format(date=date, link=link)


def index_by_title(index: Index) -> str:
    groups = []
    for letter, stories in groupby(sorted(index.stories.values()), initial_letter):
        items = map(alphabetical_item, stories)
        group = ALPHABETICAL_GROUP.format(letter=letter, entries=''.join(items))
        groups.append(group)
    return ALPHABETICAL_INDEX.format(groups=''.join(groups))


MONTH_GROUP = r'''
    <div id="{label}">
        <h2>{date}</h2>
        <div>
        {entries}
        </div
    </div>
'''

YEAR_HEADER = r'''
    <div id="{label}">
        <h2>{date}</h2>
        <div>
        {entries}
        </div
    </div>
'''

YEARS_MONTH_LINKS = r'''
    <h2>{year} {months}</h2>
'''


def index_by_date(index: Index) -> str:
    months = []
    for date_str, stories in groupby(index.stories.values(), year_month):
        entries = [f'<p>{xhtml_string(stories.title_link)}</p>\n' for story in stories]
        label = date.strftime('month-%Y-%m')
        date = date.strftime("%B %Y")
        months.append(MONTH_GROUP.format(entries, ''.join(entries), date=date, label=label))





def initial_letter(story: Story) -> str:
    return story._sorting_key[0].upper()


if __name__ == '__main__':
    main()
