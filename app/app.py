import datetime
import json
import re
from pprint import pprint
from flask import Flask, render_template

from database.models import Entry, Card
from client import Client

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
    text = re.sub(r'\`([^\`\s]*)\`', r'<code class="inline-snippet">\1</code>', text)
    return text

def block_to_html(block):
    print(block.type)
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

    elif block.type == 'column_list':
        for elem in block.children:
            if hasattr(elem, 'title'):
                print(elem.title)
            for sub_elem in block.children:
                if hasattr(sub_elem, 'title'):
                    print(sub_elem.title)

        return 'ColumnList'
    elif block.type == 'code':
        return '<pre><code class="java">{title}</code></pre>'.format(title=block.title)
    elif block.type == 'image':
        return '<img src="{source}" height="{height}" width="{width}"/>'.format(
            source=block.source,
            height=block.height,
            width=block.width
        )
    elif block.type == 'video':
        return ''
    elif block.type == 'drive':
        return ''
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

app.run('127.0.0.1', 5000)
