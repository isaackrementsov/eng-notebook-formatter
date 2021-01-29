from notion.client import NotionClient


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


# Class to store card body and properties
class Card:

    def __init__(self, props, content):
        # Card properties
        self.props = props

        # Blocks in the goal section
        self.goal = []
        # Engineering notebook entries
        self.entries = []
        # Section counter
        j = -1
        # Divider index for reference within sections
        div_index = 0

        blocks = content.children
        last = len(blocks) - 1

        for i in range(len(blocks)):
            block = blocks[i]
            type = block.type
            print(type)
            if type == 'divider' and i != last:
                divider_index = i
                j += 1
            else:
                if j == -1:
                    self.goal.append(block)
                else:
                    if i - divider_index == 1:
                        self.entries.append([block])
                    else:
                        self.entries[j].append(block)

    def get_block_url(props):
        # Get the properly formatted row id
        id = ''.join(props.id.split('-'))
        # URL to find that row as a page
        return 'https://www.notion.so/' + props.title + '-' + id
