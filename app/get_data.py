import json
import pickle
from client import Client
from database.models import Card, save

credentials = json.load(open('credentials.json', 'r'))
Client(token_v2=credentials['token'])

# Sprint 2: https://www.notion.so/dc442ead4ce24653b3fbbec56c9da987?v=7ee74fbb66e64423becf2885396e6987
# Sprint 3: https://www.notion.so/0d616b287ebf4a10bff7b49f022a9c1a?v=322ad6c60e124d8b88ba2ad1a03d18a8
# Sprint 4: https://www.notion.so/8140622829a94476b79b722c227b5bf8?v=39710217e7d94b03b64137dc5748d3ff
# Sprint 4.1: https://www.notion.so/dfa154ad34184a58a314ea6b3a7fe2bd?v=32faf4de4b7c41abb5596a320333f9bf

LINKS = [
    'https://www.notion.so/dc442ead4ce24653b3fbbec56c9da987?v=7ee74fbb66e64423becf2885396e6987'
    'https://www.notion.so/0d616b287ebf4a10bff7b49f022a9c1a?v=322ad6c60e124d8b88ba2ad1a03d18a8',
    'https://www.notion.so/8140622829a94476b79b722c227b5bf8?v=39710217e7d94b03b64137dc5748d3ff',
    'https://www.notion.so/dfa154ad34184a58a314ea6b3a7fe2bd?v=32faf4de4b7c41abb5596a320333f9bf'
]

for link in LINKS:
    cards = Card.get_cards(link)

    for card in cards:
        if card.valid:
            save(card)
