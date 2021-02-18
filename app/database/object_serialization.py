from client import Client

from sqlalchemy.types import TypeDecorator, BLOB
import pickle

class PickleType(TypeDecorator):
    impl = BLOB

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = pickle.dumps(value)

        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = pickle.loads(value)

        return value

class BlockArray(PickleType):

    def process_bind_param(self, value, dialect):

        def remove_client(block):
            without_client = block

            if hasattr(without_client, 'collection'):
                without_client.collection._client = None

            without_client._client = None

            return without_client

        # Remove client attribute (cannot be serialized)
        if value is not None and len(value) > 0:
            value = [remove_client(block) for block in value]

        return super().process_bind_param(value, dialect)

    def process_result_value(self, value, dialect):

        def load_attrs(block):
            with_client = block

            if Client.instance is not None:
                with_client._client = Client.instance

                if hasattr(with_client, 'collection'):
                    with_client.collection._client = Client.instance

            return with_client

        value = super().process_result_value(value, dialect)
        value = [load_attrs(block) for block in value]

        return value
