from app import app
from models import db, State, City, User, Official, Question, CityOfficial
from utility import get_channel
import requests

db.drop_all()
db.create_all()

states = [
    'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 
    'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 
    'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 
    'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 
    'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 
    'VA', 'WA', 'WV', 'WI', 'WY'
]
state_objects = {}
for i, state in enumerate(states, start=1):
    state_objects[state] = State(id=i, name=state)

db.session.add_all(state_objects.values())
db.session.commit()
