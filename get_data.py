import json
from client import Client


credentials = json.load(open('credentials.json', 'r'))
client = Client(token_v2=credentials['token_v2'])

cards = client.get_cards('https://www.notion.so/dc442ead4ce24653b3fbbec56c9da987?v=7ee74fbb66e64423becf2885396e6987')

for card in cards:
    # These are the properties at the top of each card
    print(card.props)
    # These are the notion "blocks" in the card's body
    print(card.blocks)
