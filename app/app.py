import datetime
import time
import json
import re
import urllib
import timeago
import requests
from flask import Flask, render_template, redirect

from database.models import Entry, Card
from client import Client
from pdf_conversion import page_to_pdf

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

cookie = 'notion_browser_id=998a835a-33c5-4989-a880-a82dbc94f35d; notion_locale=en-US%2Flegacy; ajs_anonymous_id=%22e17535c7-741a-4930-9005-92bb54c7082d%22; intercom-id-gpfdrxfd=8acb8695-82b2-4dcd-a74f-6c79726d8d27; token_v2=d19c7ce73e9c7d191d45c57532c9827ad98985d72f4a138988bd00e34f5a3d648ccaca7a3dce2a41e09849fe4e9be3b7c830f6e7990e50f2addbce04412a8176fc83d400c611c8e3d1d862da2dd5; notion_user_id=6956a63c-9587-4e5c-9557-71412c200a68; notion_users=%5B%226956a63c-9587-4e5c-9557-71412c200a68%22%5D; ajs_user_id=%226956a63c95874e5c955771412c200a68%22; ajs_group_id=%22e7e8ab80cf1b43d4a7650d4c76c13082%22; __cfduid=d5edf93f90aeda60eb714b83471f0cbde1612561730; __stripe_mid=127d5e6a-9c02-4164-b75d-cb35b04c61a5a10687; intercom-session-gpfdrxfd=cEJaYURiQ3ZmWkhUUWQ0TWlhdjJHZzFjSnJrNmxHMC9QSXZvbDFzd1ZVYzhCSlNlbXBBallEaDlCTVc3Q1BTUC0tanJXK3UxNkFZZUFyeVVoaW0zem11Zz09--737ff397b639980cbfc673aebd4e49f1665f1487; logglytrackingsession=f458c0dc-785e-4a2d-9f90-c645b6992890'

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

def make_auto(dimension):
    return 'auto' if dimension is None else dimension

def extract_equations(fragments):
    equations = []

    for fragment in fragments:
        if len(fragment) > 1:
            formatting = fragment[1]
            eq = [option for option in formatting if option[0] == 'e']

            if len(eq) > 0:
                latex = eq[0][1]
                equations.append(latex)

    return equations

def mathy_title(block, original):
    slices = original.split('⁍')

    if len(slices) > 1:
        fragments = block.get()['properties']['title']
        equations = extract_equations(fragments)

        title = ''
        inline = original.replace(' ', '') == '⁍'
        for i in range(len(slices)):
            title += slices[i]

            if i < len(slices) - 1:
                if inline:
                    title += '$$ {equation} $$'.format(equation=equations[i])
                else:
                    title += '\( {equation} \)'.format(equation=equations[i])

        return title
    else:
        return original

def handle_formatting(block):
    text = block.title

    formatted = text.replace('<', '&lt;').replace('>', '&gt;')
    formatted = re.sub(r'\`([^\`]*)\`', r'<code class="inline-snippet">\1</code>', formatted)
    formatted = re.sub(r'\[([^\[\]]*)\]\((.*?)\)', r'<a href="\2">\1</a>', formatted)
    formatted = re.sub(r'\_\_(.*?[^\_\s])\_\_', r'<b>\1</b>', formatted)
    formatted = re.sub(r'\_(.*?[^\_\s])\_', r'<i>\1</i>', formatted)
    formatted = mathy_title(block, formatted)

    return formatted

def get_image_url(url, block):
    encoded = urllib.parse.quote(str(url), safe='~()*!.\'')
    new_url = 'https://www.notion.so/image/{encoded}?table={table}&id={id}&cache=v2'.format(
        encoded=encoded,
        table='block' if block.parent._table == 'space' else block.parent._table,
        id=block.id
    )

    return new_url

def download_image(url, path):
    res = requests.get(url, headers={'cookie': cookie}, stream=True)
    ext = url.split('?')[0].split('.')[-1]

    with open('./app' + path, 'wb') as file:
        for chunk in res:
            file.write(chunk)

    del res

def block_to_html(block):
    try:
        type = block.type

        if type == 'bookmark':
            cover = ''

            if block.bookmark_cover:
                cover = '/static/img/bookmark/bg_{id}.jpg'.format(id=block._id)
                download_image(block.bookmark_cover, cover)

            return """<div style="display: flex">
                <a class="web-bookmark" href="{link}" style="background-image: url({cover})">
                    <p>
                        <span class="bookmark-title">{title}</span>
                        <span class="bookmark-description">{description}</span>
                    </p>
                </a>
            </div>""".format(
                link=block.link,
                cover=cover,
                title=block.title,
                description=shorten(block.description, 65)
            )
        elif type.split('_')[-1] == 'list' and type != 'column_list':
            return '<li class="list-elem">{title}</li>'.format(title=handle_formatting(block))
        elif type == 'code':
            return '<pre><code class="java">{title}</code></pre>'.format(title=block.title)
        elif type == 'image':
            return '<img src="{source}" height="{height}" width="{width}"/>'.format(
                source=block.source,
                height=make_auto(block.height),
                width=make_auto(block.width)
            )
        elif type == 'column_list':
            column_list = '<div class="column-list">'

            for child in block.children:
                column = '<div class="column">'

                for grandchild in child.children:
                    column += block_to_html(grandchild)

                column_list += column + '</div>'

            return column_list + '</div>'
        elif type == 'video':
            ext = block.source.split('?')[0].split('.')[-1]
            mime = mimes.get(ext)

            if mime is None:
                return '<iframe height="300" width="500" src="{source}"></iframe>'.format(source=block.source.replace('watch?v=', 'embed/'))
            else:
                '''
                return """<video height="{height}" width="{width}" controls>
                    <source src="{source}" type="{mime}"/>
                </video>""".format(
                    height=block.height,
                    width=block.width,
                    source=block.source,
                    mime=mimes.get(ext)
                )
                '''
                return ''
        elif type == 'drive':
            record = block.get()
            thumbnail = ''
            title = ''
            icon = ''
            user = ''
            timestamp = ''
            source = ''
            props = record['format'].get('drive_properties')

            if props is not None:
                if props.get('thumbnail'):
                    url = get_image_url(props['thumbnail'], block)
                    thumbnail = '/static/img/drive/bg_{id}.jpg'.format(id=block._id)
                    download_image(url, thumbnail)

                if props.get('modified_time'):
                    timestamp = timeago.format(
                        datetime.datetime.fromtimestamp(int(props['modified_time']) / 1e3),
                        datetime.datetime.now()
                    )

                source = props.get('url')
                icon = props.get('icon')
                title = props.get('title')
                user = props.get('user_name')

            return """<div style="display: flex">
                <a class="web-bookmark drive-preview" href="{source}" style="background-image: url({thumbnail})">
                    <p>
                        <span class="bookmark-title"><img src="{icon}"/>{title}</span>
                        <span class="bookmark-edited">Last edited by {user} {timestamp}</span>
                    </p>
                </a>
            </div>""".format(
                source=source,
                thumbnail=thumbnail,
                icon=icon,
                title=title,
                user=user,
                timestamp=timestamp
            )
        elif hasattr(block, 'title'):
            if block.title.replace(' ', '') != '':
                return '<p>{title}</p>'.format(title=handle_formatting(block))

        return ''
    except Exception as e:
        print(e)
        print('Too many requests; waiting 10 seconds')
        time.sleep(10)
        print('Continuing...')

        return block_to_html(block)

def shorten(text, max_len):
    shortened = text[0:max_len]

    if len(text) > max_len:
        shortened += '..' if text[-1] == '.' else '...'

    return shortened

@app.route('/generate_page', methods=['GET'])
def generate_page():
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

@app.route('/generate_supp', methods=['GET'])
def generate_supp():
    important_cards = Card.get_important()

    return render_template(
        'supplemental_notebook.html',
        important_cards=important_cards,
        block_to_html=block_to_html
    )

@app.route('/saved', methods=['GET'])
def display_saved():
    return render_template('saved.html')

@app.route('/pdf', methods=['GET'])
def handle_pdf():
    doc = page_to_pdf('http://localhost:5000/saved')
    redirect('/static/img/' + doc)

app.run('127.0.0.1', 5000)
