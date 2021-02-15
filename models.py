import datetime

from sqlalchemy import Column, Integer, String, ARRAY, ForeignKey
#from sqlalchemy.types import PickleType
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

from object_serialization import PickleType
from connect import session

# SQLAlchemy base model
Base = declarative_base()

def save(obj):
    session.add(obj)
    session.commit()

# Class to store card body and properties
class Card(Base):

    __tablename__ = 'card'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    type = Column(PickleType)
    assign = Column(PickleType)
    goal = Column(PickleType)
    entries = relationship('Entry', back_populates='card')

    def __init__(self, row, content):
        self.initialize(row, content)
        self.valid = len(self.goal) > 0

    def initialize(self, props, content):
        # Card properties
        self.title = props.title.encode('utf-8')

        self.assign = []
        for person in props.assign:
            self.assign.append(person.full_name)

        # TODO: convert all cards from type -> teams
        self.type = props.teams
        self.props = props

        # Blocks in the goal section
        self.goal = []
        # Engineering notebook entries
        self.entries = []
        # Section counter
        j = -1
        # Divider index for reference within sections
        divider_index = 0

        blocks = content.children
        last = len(blocks) - 1

        for i in range(len(blocks)):
            block = blocks[i]
            type = block.type

            if type == 'divider' and i != last:
                divider_index = i
                j += 1
            else:
                if j == -1:
                    if block.type != 'sub_header':
                        block._client = None
                        self.goal.append(block)
                else:
                    if i - divider_index == 1:
                        entry = Entry(block)
                        self.entries.append(entry)
                    else:
                        self.entries[j].incorporate(block)

    def get_block_url(props):
        # Get the properly formatted row id
        id = ''.join(props.id.split('-'))
        # URL to find that row as a page
        return 'https://www.notion.so/' + props.title + '-' + id

    def getAll():
        return session.query(Card).all()

# Class to contain engineering notebook entries
class Entry(Base):

    __tablename__ = 'entry';

    id = Column(Integer, primary_key=True)

    timeframe = Column(PickleType)
    columns = Column(PickleType)
    progress = Column(PickleType)
    takeaways = Column(PickleType)
    plans = Column(PickleType)

    card_id = Column(Integer, ForeignKey('card.id'))
    card = relationship('Card', back_populates='entries')

    def __init__(self, date_block):
        self.blocks = []

        self.timeframe = self.format_timeframe(date_block.title)
        self.columns = []
        self.progress = []
        self.takeaways = []
        self.plans = []

    def format_timeframe(self, date_string):
        # Could be __date__, date1-date2, date1,date2
        date_string = date_string.replace('_', '')
        date_string = date_string.replace(' ', '')

        delimiters = ['-', ',']
        types = ['range', 'list']
        success = False
        date_sections = []
        i = 0

        while not success and i < len(delimiters):
            date_sections, success = self.try_split(date_string, delimiters[i])
            i += 1

        return {'type': types[i - 1], 'values': [self.to_date(s) for s in date_sections]}

    def to_date(self, formatted_string):
        return datetime.datetime.strptime(formatted_string, '%m/%d/%Y')

    def try_split(self, string, delimiter):
        parts = string.split(delimiter)

        return parts, len(parts) > 1

    def incorporate(self, block):
        block._client = None;
        self.blocks.append(block)
