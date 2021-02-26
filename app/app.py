import datetime
import json
import re
from pprint import pprint
from flask import Flask, render_template

from database.models import Entry, Card
from client import Client

mimes = {
    'mov': 'video/quicktime',
    'avi': 'video/x-msvideo',
    'flv': 'video/x-flv',
    'mp4': 'video/mp4',
    'm3u8': 'application/x-mpegURL',
    'ts': 'video/MP2T',
    '3gp': 'video/3gpp',
    'wmv': 'video/x-ms-wmv'
}

credentials = json.load(open('credentials.json', 'r'))
Client(token_v2=credentials['token_v2'])

app = Flask(__name__, static_url_path='/static/')

def prettify(dates):
    modified = []

    for date in dates:
        modified.append(date.strftime('%m/%d/%Y'))

    return modified

def rank_date(date):
    return datetime.datetime.strptime(date, '%m_%d_%Y')

def handle_formatting(text):
    formatted = text.replace('<', '&lt;').replace('>', '&gt;')
    formatted = re.sub(r'\`([^\`]*)\`', r'<code class="inline-snippet">\1</code>', formatted)
    formatted = re.sub(r'\[([^\[\]]*)\]\((.*?)\)', r'<a href="\2">\1</a>', formatted)
    formatted = re.sub(r'\_\_(.*?[^\_\s])\_\_', r'<b>\1</b>', formatted)
    formatted = re.sub(r'\_(.*?[^\_\s])\_', r'<i>\1</i>', formatted)

    return formatted

def block_to_html(block):
    if block.type == 'bookmark':
        return """<div style="display: flex">
            <a class="web-bookmark" href="{link}" style="background-image: url({cover})">
                <p>
                    <span class="bookmark-title">{title}</span>
                    <span class="bookmark-description">{description}</span>
                </p>
            </a>
        </div>""".format(
            link=block.link,
            cover=block.bookmark_cover,
            title=block.title,
            description=shorten(block.description, 65)
        )
    elif block.type.split('_')[-1] == 'list' and block.type != 'column_list':
        return '<li class="list-elem">{title}</li>'.format(title=handle_formatting(block.title))
    elif block.type == 'code':
        return '<pre><code class="java">{title}</code></pre>'.format(title=block.title)
    elif block.type == 'image':
        return '<img src="{source}" height="{height}" width="{width}"/>'.format(
            source=block.source,
            height=block.height,
            width=block.width
        )
    elif block.type == 'column_list':
        return ''
    elif block.type == 'video':
        ext = block.source.split('?')[0].split('.')[-1]
        mime = mimes.get(ext)

        if mime is None:
            return '<iframe height="300" width="500" src="{source}"></iframe>'.format(source=block.source.replace('watch?v=', 'embed/'))
        else:
            return """<video height="{height}" width="{width}" controls>
                <source src="{source}" type="{mime}"/>
            </video>""".format(
                height=block.height,
                width=block.width,
                source=block.source,
                mime=mimes.get(ext)
            )
    elif block.type == 'drive':
        record = block.get()
        thumbnail = ''
        title = ''
        props = record['format'].get('drive_properties')

        if props is not None:
            thumbnail = props['thumbnail']
            title = props['title']

        return """<div style="display: flex">
            <a class="web-bookmark drive-preview" href="{source}" style="background-image: url({thumbnail})">
                <p>
                    <span class="bookmark-title">{title}</span>
                </p>
            </a>
        </div>""".format(
            source=block.source,
            thumbnail=thumbnail,
            title=title
        )
    elif hasattr(block, 'title'):
        if block.title.replace(' ', '') != '':
            return '<p>{title}</p>'.format(title=handle_formatting(block.title))

    return block.type

def shorten(text, max_len):
    shortened = text[0:max_len]

    if len(text) > max_len:
        shortened += '..' if text[-1] == '.' else '...'

    return shortened

@app.route('/', methods=['GET'])
def display():
    entries = Entry.get_all()

    entry_map = Entry.group_by_date(entries)
    dates = entry_map.keys()
    dates = sorted(dates, key=rank_date)

    sprint_goals = Card.group_by_sprint(entries)

    return render_template(
        'main_notebook.html',
        entry_map=entry_map,
        dates=dates,
        sprint_goals=sprint_goals,
        block_to_html=block_to_html,
        prettify=prettify
    )

@app.route('/drive', methods=['GET'])
def test_gdrive():
    return render_template('gdrive_test.html')

app.run('127.0.0.1', 5000)
