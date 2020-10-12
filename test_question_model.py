"""Question model tests."""

# to run:
#    python -m unittest test_question_model.py


import os
from unittest import TestCase

from models import db, User, City, State, Official, Question

# DB for testing
os.environ['DATABASE_URL'] = "postgresql:///saber_db_test"


from app import app

db.drop_all()
db.create_all()

from sqlalchemy.exc import IntegrityError

class QuestionModelTestCase(TestCase):
    """Question model test cases"""

    @classmethod
    def setUpClass(cls):

        # Create a city/state to use later
        state1 = State(id=1, name='PA')
        city1 = City(id=1, name='Philadelphia', state_id=1)
        official1 = Official(id=1, name='Official', office='Mayor')
        user1 = User(
            id=1,
            username='testuser',
            password='password',
            email='test@user.com',
            city_id=1
        )
        db.session.add_all([state1, city1, official1, user1])
        db.session.commit()

    def setUp(self):
        try:
            db.session.query(Question).delete()
            db.session.commit()
        except:
            db.session.rollback()
        
        self.client = app.test_client()

    def test_question_model_instance(self):
        """Test question model instance"""
        question = Question(
            id=1,
            user_id=1,
            official_id=1,
            text='This is a text question.',
        )
        db.session.add(question)
        db.session.commit()

        self.assertEqual(len(Question.query.all()), 1)
        self.assertEqual(question.user.city.name, 'Philadelphia')
        self.assertFalse(question.answered)


        