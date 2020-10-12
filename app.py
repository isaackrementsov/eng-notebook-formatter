import json
from notion.client import NotionClient
from flask import Flask, render_template, request

import notion_html

# Initialize Flask app
app = Flask(__name__)

credentials = json.load(open('credentials.json', 'r'))

# Use token_v2 from Notion cookies while logged in to access API
client = NotionClient(token_v2=credentials['token'])
html_generator = notion_html.HTMLGenerator(client)

# Return notion output via Flask route
@app.route('/')
def get_notion_output():
    html = html_generator.get_sprint_html()
    return render_template('index.html', html=html)
