"""Test view functions"""

# run these tests with:
#
#     python -m unittest test_views.py

import os
from unittest import TestCase
from app import app, CURR_USER_KEY
from models import db, User, City, State, Official, Question, CityOfficial

# DB for testing
os.environ['DATABASE_URL'] = "postgresql:///saber_db_test"

app.config['WTF_CSRF_ENABLED'] = False

db.drop_all()
db.create_all()

from sqlalchemy.exc import IntegrityError

class ViewsTestCase(TestCase):
    """Test cases for Flask views"""

    @classmethod
    def setUpClass(cls):

        # Create a city/state to use later
        state1 = State(id=1, name='PA')
        city1 = City(id=1, name='Philadelphia', state_id=1)
        o1 = Official(id=1, name='Mr. Official', office='Mayor')
        db.session.add_all([state1, city1, o1])
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
        co1 = CityOfficial(city_id=1, official_id=1)
        db.session.add(co1)
        db.session.commit()

    def setUp(self):
        Question.query.delete() # Clear questions table before each test
        db.session.commit()
    
    def tearDown(self):
        db.session.rollback() # roll back transactions

    def show_profile(self):
        """Can user see their profile?"""
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = 1 # log in

            resp = client.get('/profile', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('testuser', html)
            self.assertIn('Philadelphia, PA', html)

    def show_profile_no_login(self):
        """Can unauthorized user see their profile?"""
        with app.test_client() as client:

            resp = client.get('/profile', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Access unauthorized.', html)

    def test_show_officials(self):
        """Can user see officials list?"""
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = 1 # log in

            resp = client.get('/officials', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Mr. Official', html)

    def test_show_officials_no_login(self):
        """Does user get redirected when not logged in?"""
        with app.test_client() as client:
            resp = client.get('/officials', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Access unauthorized.', html)

    def test_new_question(self):
        """Can user post a new question?"""
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = 1

            resp = client.post('/new', data={'official': 1, 'text': 'Test Question!'})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            question = Question.query.one()
            self.assertEqual(question.text, 'Test Question!')

    def test_new_question_no_login(self):
        """Can unauthorized user post a new question?"""
        with app.test_client() as client:
            resp = client.post('/new', data={'official': 1, 'text': 'Test Question!'}, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Access unauthorized.', html) # Make sure redirected

            questions = Question.query.all() # Make sure no questions were posted
            self.assertEquals(len(questions), 0)






    

    