"""User model tests."""

# to run:
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, City, State, Official, Question

# DB for testing
os.environ['DATABASE_URL'] = "postgresql:///saber_db_test"


from app import app

db.drop_all()
db.create_all()

from sqlalchemy.exc import IntegrityError

class UserModelTestCase(TestCase):
    """User model test cases"""
    
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
            db.session.query(User).delete()
            db.session.commit()
        except:
            db.session.rollback()
        
        self.client = app.test_client()

    def test_user_model_instance(self):
        """Test user model instance"""
        db.session.query(User).delete()
        db.session.commit()
        user = User(
            id=1,
            username='testuser',
            password='password',
            email='test@user.com',
            city_id=1
        )
        db.session.add(user)
        db.session.commit()

        self.assertEqual(len(User.query.all()), 1)
        self.assertEqual(user.city.name, 'Philadelphia')
        self.assertEqual(len(user.likes), 0)

    def test_user_repr(self):
        """Test repr dunder"""
        user = User(
            id=1,
            username='testuser',
            password='password',
            email='test@user.com',
            city_id=1
        )
        db.session.add(user)
        
        self.assertEqual(str(user), '<User testuser>')

    def test_signup_cls_method(self):
        """Test the signup class method"""
        user = User.signup(
            username="user1",
            email="user@test.com",
            password="HASHED_PASSWORD",
            image_url='www.www.com',
            city_id=1
        )
        db.session.commit()
        queried_user = User.query.get(user.id)
        self.assertEqual(str(queried_user), str(user))

        with self.assertRaises(IntegrityError):
            fail_user = User.signup(
                username='user1',
                email='email@email.com',
                password='pass',
                image_url='www.www.com',
                city_id=1
            )
            db.session.add(fail_user)
            db.session.commit()
   
    def test_authenticate_cls_method(self):
        """Test the signup class method"""
        fail = User.authenticate('notauser', 'pass')
        self.assertFalse(fail)

        user1 = User.signup(
            username="user1",
            email="user@test.com",
            password="HASHED_PASSWORD",
            image_url='www.www.com',
            city_id=1
        )
        db.session.commit()

        success = User.authenticate('user1', 'HASHED_PASSWORD')
        self.assertEqual(success.username, user1.username)

        fail_pass = User.authenticate('user1', 'WRONG_PASSWORD')
        self.assertFalse(fail_pass)

        fail_username = User.authenticate('user2', 'HASHED_PASSWORD')
        self.assertFalse(fail_username)
