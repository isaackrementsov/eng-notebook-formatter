import datetime
import json
from pprint import pprint
from flask import Flask, render_template

from database.models import Entry, Card
from client import Client

credentials = json.load(open('credentials.json', 'r'))
Client(token_v2=credentials['token'])

app = Flask(__name__, static_url_path='/static/')

def prettify(dates):
    modified = []

    for date in dates:
        modified.append(date.strftime('%m/%d/%Y'))

    return modified

def rank_date(date):
    return datetime.datetime.strptime(date, '%m_%d_%Y')

def block_to_html(block):
    if block.type == 'bookmark':
        print(block.bookmark_cover)
        print(block.bookmark_icon)
        print(block.title)
        print(block.caption)
        print(block.description)
        template = '<a class="web-bookmark" href="{link}" style="background-image: url({cover})">{title}</a>'
        return template.format(link=block.link, cover=block.bookmark_cover, title=block.title)
    elif block.type == 'bulleted_list':
        return ''
    elif block.title.replace(' ', '') != '':
        return '<p>{title}</p>'.format(title=block.title)

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
