from sqlalchemy import Column, Integer, String, NestedMutableJSON, ARRAY, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

# SQLAlchemy base model
Base = declarative_base()

# Class to store card body and properties
class Card(Base):

    __tablename__ = 'card'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    type = Column(ARRAY(String))
    assign = Column(ARRAY(String))
    goal = Column(NestedMutableJSON)

    def initialize(self, props, content):
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

            if type == 'divider' and i != last:
                divider_index = i
                j += 1
            else:
                if j == -1:
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


# Class to contain engineering notebook entries
class Entry(Base):

    timeframe = Column(NestedMutableJSON)
    columns = Column(ARRAY(String))
    progress = Column(NestedMutableJSON)
    takeaways = Column(NestedMutableJSON)
    plans = Column(NestedMutableJSON)

    card_id = ForeignKey()

    def __init__(self, date_block):
        self.blocks = []

    def incorporate(self, block):
        self.blocks.append(block)
