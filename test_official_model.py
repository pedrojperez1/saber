"""Official model tests."""

# to run:
#    python -m unittest test_official_model.py


import os
from unittest import TestCase

from models import db, User, City, State, Official, CityOfficial

# DB for testing
os.environ['DATABASE_URL'] = "postgresql:///saber_db_test"


from app import app

db.drop_all()
db.create_all()

from sqlalchemy.exc import IntegrityError

class OfficialModelTestCase(TestCase):
    """Official model test cases"""

    @classmethod
    def setUpClass(cls):
        # Create a city/state to use later
        state1 = State(id=1, name='PA')
        city1 = City(id=1, name='Philadelphia', state_id=1)
        user1 = User(
            id=1,
            username='testuser',
            password='password',
            email='test@user.com',
            city_id=1
        )
        db.session.add_all([state1, city1, user1])
        db.session.commit()


    def setUp(self):
        try:
            Official.query.delete()
            db.session.commit()
        except:
            db.session.rollback()
        
        self.client = app.test_client()


    def test_question_model_instance(self):
        """Test question model instance"""
        Official.query.delete()
        db.session.commit()
        official = Official(
            id=1,
            name='Test User',
            office='Test Office',
            party='Tes',
            email='test@email.com',
        )
        db.session.add(official)
        db.session.commit()

        self.assertEqual(len(Official.query.all()), 1)

    def test_cls_method_get_officials_for_city(self):
        """Test cls method get officials for city"""
        city = City.query.get(1)

        # Pings the API and asserts that officials for Philly are >= 1
        
        self.assertGreaterEqual(len(Official.get_officials_for_city(city)), 1)
