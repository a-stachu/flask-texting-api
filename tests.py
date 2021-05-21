import unittest
from app import app, db
from app.models import User, Message
from flask_webtest import TestApp
from flask_login import AnonymousUserMixin

class TestCase(unittest.TestCase):

    #SETTING UP ENVIRONMENT
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['LOGIN_DISABLED'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        self.app = app
        self.client = self.app.test_client()
        self.w = TestApp(self.app)
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    #ENSURE USER BEHAVES CORRECTLY
    def test_user(self):
        test_user = User(username='USER')
        test_user.set_password('PASSWORD')
        db.session.add(test_user)
        db.session.commit()
        assert test_user in db.session

    #ENSURE MESSAGE BEHAVES CORRECTLY
    def test_message(self):
        test_user = User(username='USER')
        test_message = Message(text='MESSAGE', user=test_user)
        db.session.add(test_message)
        db.session.commit()
        assert test_message in db.session

    #ENSURE COUNTER BEHAVES CORRECTLY WHILE VIEWING IT
    def test_message_view(self):
        test_user = User(username='USER')
        test_message = Message(text='MESSAGE', user=test_user)
        test_message2 = Message(text='MESSAGE2', user=test_user)
        db.session.add(test_message)
        db.session.add(test_message2)
        db.session.commit()
        messages = Message.query.all()
        for message in messages:
            message.counter = Message.counter + 1
        db.session.commit()
        assert test_message in db.session
        assert test_message2 in db.session

    #ENSURE MESSAGE REMOVES CORRECTLY
    def test_message_removal(self):
        test_user = User(username='USER')
        test_message = Message(text='MESSAGE', user=test_user, id=1)
        db.session.add(test_message)
        db.session.commit()
        removed_message = Message.query.filter_by(id=test_message.id, user=test_message.user).first()
        db.session.delete(removed_message)
        db.session.commit()
        assert test_message in db.session

    #ENSURE MESSAGE'S CONTENTS ARE EDITED CORRECTLY
    def test_message_edit(self):
        test_user = User(username='USER')
        test_message = Message(text='MESSAGE', user=test_user, id=1)
        db.session.add(test_message)
        db.session.commit()
        new_message = Message.query.filter_by(id=test_message.id, user=test_message.user).first()
        new_message.text = 'NEW MESSAGE'
        new_message.counter = 0
        db.session.commit()
        assert new_message in db.session
        print(test_message.text)

    #TESTING HTTP RESPONSES
    def test_pages(self):
        with app.test_client() as c:
            response = c.get('/login')
            self.assertEqual(response.status_code, 200)
            response = c.get('/logout')
            self.assertEqual(response.status_code, 302)
            response = c.get('/index')
            self.assertEqual(response.status_code, 200)
            if (AnonymousUserMixin == False):
                response = c.get('/add')
                self.assertEqual(response.status_code, 200)
                response = c.get('/edit')
                self.assertEqual(response.status_code, 200)
                response = c.get('/remove')
                self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()