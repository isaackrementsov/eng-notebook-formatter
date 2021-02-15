from sqlalchemy.types import TypeDecorator, BLOB
import pickle

class PickleType(TypeDecorator):
    impl = BLOB

    def process_bind_param(self, value, dialect):
        if value is not None:
            # Remove client attribute (cannot be serialized)
            value = pickle.dumps(value)

        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = pickle.loads(value)

        return value
