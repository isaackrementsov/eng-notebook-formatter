import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Load environment-private parameters
credentials = json.load(open('credentials.json', 'r'))
# MySQL/MariaDB user
user = credentials['db']['user']
# DB password
password = credentials['db']['password']

# SQLAlchemy engine
engine = create_engine('mysql://localhost:3310/notebook?user=' + user + '&password=' + password)

Session = sessionmaker(bind=engine)
session = Session()
