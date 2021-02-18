from notion.client import NotionClient

# Class that adds useful methods to NotionClient
class Client(NotionClient):

    instance = None

    # Use token_v2 from cookies to initialize client
    def __init__(self, token_v2):
        super().__init__(token_v2=token_v2)

        Client.instance = self
