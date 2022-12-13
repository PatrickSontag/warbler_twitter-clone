"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        user1 = User.signup("testuser1", "test1@test.com", "password1", None)
        user_id_1 = 1000
        user1.id = user_id_1

        user2 = User.signup("testuser2", "test2@test.com", "password2", None)
        user_id_2 = 2000
        user2.id = user_id_2

        db.session.commit()

        user1 = User.query.get(user_id_1)
        user2 = User.query.get(user_id_2)

        self.user1 = user1
        self.user_id_1 = user_id_1
        self.user2 = user2
        self.user_id_2 = user_id_2

        # User.query.delete()
        # Message.query.delete()
        # Follows.query.delete()

        self.client = app.test_client()
    
    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )
        db.session.add(u)
        db.session.commit()

        # User should have no messages, followers, following, or likes
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)
        self.assertEqual(len(u.following), 0)
        self.assertEqual(len(u.likes), 0)

    # Following Tests
    def test_user_following(self):
        self.user1.following.append(self.user2)
        db.session.commit()
        print(self.user2.followers)
        self.assertEqual(len(self.user2.followers), 1)
        self.assertEqual(len(self.user1.following), 1)
        self.assertEqual(len(self.user1.followers), 0)
        self.assertEqual(len(self.user2.following), 0)

    def test_is_followed_by(self):
        self.assertFalse(self.user1.is_followed_by(self.user2))

        self.user2.following.append(self.user1)
        db.session.commit()    

        self.assertTrue(self.user1.is_followed_by(self.user2))
        self.assertFalse(self.user2.is_followed_by(self.user1))


    def test_is_following(self):
        
        self.assertFalse(self.user1.is_following(self.user2))

        self.user1.following.append(self.user2)
        db.session.commit()

        self.assertTrue(self.user1.is_following(self.user2))
        self.assertFalse(self.user2.is_following(self.user1))


    # Signup Tests
    def test_valid_signup(self):
        u_test = self.user1
        self.assertEqual(u_test.username, "testuser1")
        self.assertEqual(u_test.email, "test1@test.com")
        self.assertNotEqual(u_test.password, "password1")
        # Bcrypt strings should start with $2b$
        self.assertTrue(u_test.password.startswith("$2b$"))

    def test_invalid_username_signup(self):
        invalid = User.signup(None, "test@test.com", "password", None)
        uid = 123456789
        invalid.id = uid
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_email_signup(self):
        invalid = User.signup("testtest", None, "password", None)
        uid = 123789
        invalid.id = uid
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()
    
    def test_invalid_password_signup(self):
        with self.assertRaises(ValueError) as context:
            User.signup("testtest", "email@email.com", "", None)
        
        with self.assertRaises(ValueError) as context:
            User.signup("testtest", "email@email.com", None, None)

    
    #Authentication Tests
    def test_valid_authentication(self):
        u = User.authenticate(self.user1.username, "password1")
        self.assertIsNotNone(u)
        self.assertEqual(u.id, self.user_id_1)
    
    def test_invalid_username(self):
        self.assertFalse(User.authenticate("badusername", "password1"))

    def test_wrong_password(self):
        self.assertFalse(User.authenticate(self.user1.username, "badpassword"))