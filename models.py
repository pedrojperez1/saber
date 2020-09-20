import requests
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from flask_bcrypt import Bcrypt
from utility import get_channel, PLACEHOLDER_IMG
from config import API_KEY

db = SQLAlchemy()
bcrypt = Bcrypt()

def connect_db(app):
    db.app = app
    db.init_app(app)

# ==================================
# Core data models
# ==================================

class User(db.Model):
    """User model"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    image_url = db.Column(db.String(200), default=PLACEHOLDER_IMG)
    first_joined = db.Column(db.DateTime(timezone=True), server_default=func.now())
    last_updated = db.Column(db.DateTime(timezone=True), onupdate=func.now())
    city_id = db.Column(db.ForeignKey('cities.id'))

    # Relationships
    city = db.relationship('City', backref='users')
    likes = db.relationship('Question', secondary='likes')

    @classmethod
    def signup(cls, username, password, email, image_url, city_id):
        """class method for registering users"""
        hashed = bcrypt.generate_password_hash(password)
        hashed_utf8 = hashed.decode('utf8')

        user = cls(
            username=username,
            password=hashed_utf8,
            email=email,
            image_url=image_url,
            city_id=city_id
        )
        db.session.add(user)
        return user
        
    @classmethod
    def authenticate(cls, username, pwd):
        """Validate user exists and password is correct"""

        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, pwd):
            return user
        else:
            return False


    def __repr__(self):
        return f'<User {self.username}>'


class Official(db.Model):
    """Official model"""
    __tablename__ = 'officials'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    office = db.Column(db.String(100), nullable=False)
    party = db.Column(db.String(3))
    email = db.Column(db.String(100))
    photo_url = db.Column(db.String(200), default=PLACEHOLDER_IMG)
    twitter = db.Column(db.String(100))
    facebook = db.Column(db.String(100))

    @classmethod
    def get_officials_for_city(cls, city):
        """
        Queries the Google Civic Information API to get officials for a given city/state.
        More details: https://developers.google.com/civic-information/docs/using_api
        """
        city_name = city.name
        state_name = city.state.name
        base_url = 'https://www.googleapis.com/civicinfo/v2/'
        json_resp = requests.get(
            f'{base_url}representatives?key={API_KEY}&address={city_name}%20{state_name}'
            ).json()

        new_officials = []
        # first parse the returned list of officials for new user
        for official in json_resp['officials']:
            party = official['party'][0:3] if official.get('party') else None
            email = official['emails'][0] if official.get('emails') else None
            channels = official.get('channels')
            if channels:
                twitter = get_channel(channels, 'Twitter')
                facebook = get_channel(channels, 'Facebook')
            else: 
                twitter = facebook = None
            
            new_official = cls(
                name=official['name'],
                office='temp',
                party=party,
                email=email,
                photo_url=official.get('photoUrl'),
                twitter=twitter,
                facebook=facebook
            )
            new_officials.append(new_official)
            
        # add the offices for each official
        for office in json_resp['offices']:
            for o in office['officialIndices']:
                new_officials[o].office = office['name']
        
        # finally, before writing to DB, filter out officials that already exist
        all_officials = Official.query.all()
        to_add = [o for o in new_officials if o not in all_officials]
        # add the city <> official relationship before filtering existing officials
        to_add_city_relationship = [o for o in all_officials if o in new_officials]
        city.officials.extend(to_add_city_relationship)
        db.session.commit()

        return to_add

    def __repr__(self):
        return f'<Official {self.name}: {self.office} ({self.party}), {self.email}>'

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return repr(self) == repr(other)
        else:
            return False


class Question(db.Model):
    """Question model"""
    __tablename__ = 'questions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.ForeignKey('users.id'), nullable=False)
    official_id = db.Column(db.ForeignKey('officials.id'), nullable=False)
    text = db.Column(db.String(200), nullable=False)
    answered = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())

    # Relationships
    user = db.relationship('User', backref='questions')
    official = db.relationship('Official', backref='questions')

class Like(db.Model):
    """Like model"""
    __tablename__ = 'likes'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.ForeignKey('users.id'), nullable=False)
    question_id = db.Column(db.ForeignKey('questions.id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())

    # Relationship
    question = db.relationship('Question', backref='likes')

# ==================================
# Helper models
# ==================================
class City(db.Model):
    """City model"""
    __tablename__ = 'cities'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    state_id = db.Column(db.ForeignKey('states.id'), nullable=False)

    state = db.relationship('State', backref='cities')
    officials = db.relationship('Official', secondary='cities_officials')

    @classmethod
    def get_city_from_query(cls, city_query, state_id):
        capitalized_city = " ".join([word.capitalize() for word in city_query.split(" ")])
        city_query = City.query.filter_by(name=capitalized_city, state_id=state_id).first()

        if city_query is None: # create new city if it doesn't exist
            new_city = cls(
                name=capitalized_city,
                state_id=state_id
            )
            db.session.add(new_city)
            db.session.commit()
            new_city_officials = Official.get_officials_for_city(new_city)
            db.session.add_all(new_city_officials)
            new_city.officials.extend(new_city_officials)
            db.session.commit()
            return new_city
        else:
            return city_query


class State(db.Model):
    """State model"""
    __tablename__ = 'states'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

class CityOfficial(db.Model):
    """CityOfficial model"""
    __tablename__ = 'cities_officials'

    city_id = db.Column(db.Integer, db.ForeignKey('cities.id'), primary_key=True)
    official_id = db.Column(db.Integer, db.ForeignKey('officials.id'), primary_key=True)

