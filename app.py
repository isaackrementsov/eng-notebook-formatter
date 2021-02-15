from flask import Flask, render_template

from models import Card

app = Flask(__name__, static_url_path='/static/')

def prettify(dates):
    modified = []

    for date in dates:
        modified.append(date.strftime('%m/%d/%Y'))

    return modified

@app.route('/', methods=['GET'])
def display():
    cards = Card.getAll()

    return render_template('index.html', cards=cards, prettify=prettify)

app.run('127.0.0.1', 5000)
