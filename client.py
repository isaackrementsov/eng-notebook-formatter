from notion.client import NotionClient
from models import Card

# Class that adds useful methods to NotionClient
class Client(NotionClient):

    # Use token_v2 from cookies to initialize client
    def __init__(self, token_v2):
        super().__init__(token_v2=token_v2)

    # Get all cards from a database
    def get_cards(self, collection_url):
        cv = self.get_collection_view(collection_url)
        cards = []

        # Get each row in the collection
        for row in cv.collection.get_rows():
            # Get the content associated with each row
            content = self.get_block(Card.get_block_url(row))
            # Initialize a card object
            card = Card(row, content)

            cards.append(card)

        return cards
