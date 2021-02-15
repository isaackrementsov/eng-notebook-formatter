import json
from client import Client
from models import save

credentials = json.load(open('credentials.json', 'r'))
client = Client(token_v2=credentials['token'])

cards = client.get_cards('https://www.notion.so/dc442ead4ce24653b3fbbec56c9da987?v=7ee74fbb66e64423becf2885396e6987')

for card in cards:
    save(card)

i = 2
print(cards[i].props.title)
print(cards[i].entries)
