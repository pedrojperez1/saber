"""CityOfficial model tests."""

# to run:
#    python -m unittest test_city_official_model.py


import os
from unittest import TestCase

from models import db, User, City, State, Official, CityOfficial

# DB for testing
os.environ['DATABASE_URL'] = "postgresql:///saber_db_test"


from app import app

db.drop_all()
db.create_all()

from sqlalchemy.exc import IntegrityError

class CityOfficialModelTestCase(TestCase):
    """CityOfficial model test cases"""

    @classmethod
    def setUpClass(cls):

        # Create a city/state to use later
        state1 = State(id=1, name='PA')
        db.session.add(state1)
        db.session.commit()
        city1 = City(id=1, name='Philadelphia', state_id=1)
        db.session.add(city1)
        db.session.commit()
        o1 = Official(id=1, name='Official', office='Mayor')
        db.session.add(o1)
        db.session.commit()

    def setUp(self):
        try:
            CityOfficial.query.delete()
            db.session.commit()
        except:
            db.session.rollback()
        
        self.client = app.test_client()

    def test_city_official_model_instance(self):
        """Test CityOfficial model instance"""
        city_official = CityOfficial(city_id=1, official_id=1)
        db.session.add(city_official)
        db.session.commit()

        self.assertEqual(len(CityOfficial.query.all()), 1)
        
        philly = City.query.get(1)
        self.assertEqual(len(philly.officials), 1)