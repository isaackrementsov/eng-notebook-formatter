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

    def initialize(self, props, content):
        # Card properties
        self.title = props.title

        self.assign = {'values': []}
        for person in props.assign:
            self.assign.get('values').append(person.full_name)

        # TODO: convert all cards from type -> teams
        self.type = {'values': props.teams}
        self.props = props

        # Blocks in the goal section
        self.goal = {'values': []}
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

            if type == 'divider' and i != last:
                divider_index = i
                j += 1
            else:
                if j == -1:
                    pass
                    #self.goal.get('values').append(block)
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

    def __init__(self, date_block,):
        self.blocks = []

        self.timeframe = {'type': 'range', 'values': [320230303, 230230230]}
        self.columns = {'values': []}
        self.progress = ''
        self.takeaways = ''
        self.plans = ''

    def incorporate(self, block):
        self.blocks.append(block)
