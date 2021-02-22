import datetime
import re

from sqlalchemy import Column, Integer, String, ARRAY, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

from client import Client

from database.object_serialization import PickleType, BlockArray
from database.connect import session
from database.util import EntryTypes

n_sprints = 4

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
    goal = Column(BlockArray)

    entries = relationship('Entry', back_populates='card')

    def __init__(self, row, content):
        success = self.initialize(row, content)

        self.valid = len(self.goal) > 0

    def initialize(self, props, content):
        # Card properties
        self.title = props.title.encode('utf-8')
        # People assigned to card
        self.assign = []
        # Blocks in the goal section
        self.goal = []
        # Engineering notebook entries
        self.entries = []

        duplicate = Card.get_by_title(self.title)

        if duplicate is None:
            for person in props.assign:
                self.assign.append(person.full_name)

            self.type = props.teams
            self.props = props
        else:
            self = duplicate

        self.add_content(content)

    def remove_empty(self, blocks):
        def is_empty(block):
            if hasattr(block, 'title') and block.type == 'text':
                return block.title.replace(' ', '') == ''
            else:
                return False

        filtered = []

        for block in blocks:
            if not is_empty(block):
                filtered.append(block)

        return filtered

    def add_content(self, content):
        initial_entries = len(self.entries)
        # Section counter
        j = -1
        # Divider index for reference within sections
        divider_index = 0

        blocks = content.children
        last = len(blocks) - 1

        blocks = self.remove_empty(blocks)

        for i in range(len(blocks)):
            block = blocks[i]
            type = block.type

            if type == 'divider' and i != last:
                divider_index = i
                j += 1
            else:
                if j == -1 and initial_entries == 0:
                    if type != 'sub_header':
                        self.goal.append(block)
                elif j > -1:
                    if i - divider_index == 1:
                        entry = Entry(block)
                        self.entries.append(entry)
                    else:
                        self.entries[j + initial_entries].incorporate(block)

    def get_block_url(props):
        # Get the properly formatted row id
        id = ''.join(props.id.split('-'))
        # URL to find that row as a page
        return 'https://www.notion.so/' + props.title + '-' + id

    # Get all cards from a database
    def get_cards(collection_url):
        cv = Client.instance.get_collection_view(collection_url)
        cards = []

        # Get each row in the collection
        for row in cv.collection.get_rows():
            # Get the content associated with each row
            content = Client.instance.get_block(Card.get_block_url(row))

            # Initialize a card object
            if not str(row.status) in ['PR and Reminders', 'None']:
                card = Card(row, content)
                cards.append(card)

        return cards

    def get_all():
        return session.query(Card).all()

    def get_by_title(title):
        return session.query(Card).filter_by(title=title).first()

    def group_by_sprint(entries):
        group = [[] for i in range(n_sprints)]
        added = []

        def matches_id(id):
            return lambda card: card.id == id

        for entry in entries:
            try:
                existing_idx = added.index(entry.card_id)
            except ValueError as e:
                group[entry.sprint - 1].append(entry.card)
                added.append(entry.card_id)

        return group


entryTypes = EntryTypes({
    'progress': ['what i did', 'what we did', 'progress'],
    'takeaways': ['what i learned', 'what we learned', 'takeaways'],
    'plans': ['next steps', 'plans']
})

# Class to contain engineering notebook entries
class Entry(Base):

    __tablename__ = 'entry';

    id = Column(Integer, primary_key=True)
    sprint = Column(Integer)

    timeframe = Column(PickleType)
    columns = Column(PickleType)
    progress = Column(BlockArray)
    takeaways = Column(BlockArray)
    plans = Column(BlockArray)

    card_id = Column(Integer, ForeignKey('card.id'))
    card = relationship('Card', back_populates='entries')

    def __init__(self, date_block):
        self.section = ''

        self.timeframe = self.format_timeframe(date_block.title)
        self.columns = []
        self.progress = []
        self.takeaways = []
        self.plans = []
        self.has_columns = False

        self.sprint_dates = ['10/7/2020', '11/20/2020', '12/22/2020']
        self.sprint_dates = [self.to_date(d) for d in self.sprint_dates]

        self.sprint = self.get_sprint(self.timeframe['values'][0])

    def get_sprint(self, date):
        for i in range(len(self.sprint_dates)):
            sprint_end_date = self.sprint_dates[i]

            if date < sprint_end_date:
                return i + 1

        return i + 2

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

        return {'type': types[i - 1], 'values': [self.to_date(s) for s in date_sections if s.replace(' ', '') != '']}

    def to_date(self, formatted_string):
        return datetime.datetime.strptime(formatted_string, '%m/%d/%Y')

    def try_split(self, string, delimiter):
        parts = string.split(delimiter)

        return parts, len(parts) > 1

    def incorporate(self, block):

        def is_italic(block):
            if hasattr(block, 'title'):
                if len(block.title) > 0:
                    return block.title[0] == '_'
            else:
                return False

        if not self.has_columns and is_italic(block):
            columns = ['Not Started', 'Ideation', 'Prototyping', 'Testing', 'Final Design', 'Done']
            title = block.title.lower()

            for column in columns:
                if column.lower() in title:
                    self.columns.append(column)

        if block.type == 'text':
            label = entryTypes.get_label(block.title)

            if label:
                self.section = label
        elif self.section != '':
            current_section = getattr(self, self.section)
            current_section.append(block)

            setattr(self, self.section, current_section)

        self.has_columns = True

    def get_all():
        return session.query(Entry).all()

    def group_by_date(entries):
        group = {}

        for entry in entries:
            key = entry.timeframe['values'][0].strftime('%m_%d_%Y')

            if group.get(key):
                group[key].append(entry)
            else:
                group[key] = [entry]

        return group
