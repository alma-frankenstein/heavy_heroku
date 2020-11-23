from datetime import datetime, timedelta
import unittest
from heavy_app import app, db
from models import User, Song

class UserModelCase(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI']='sqlite://'  # create scratch database for testing
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_password_hashing(self):
        u = User(username='susan')
        u.set_password('cat')
        self.assertFalse(u.check_password('dog'))
        self.assertTrue(u.check_password('cat'))

    def test_follow(self):
        u1 = User(username='john')
        u2 = User(username='susan')
        db.session.add(u1)
        db.session.add(u2)
        self.assertEqual(u1.followed.all(), [])
        self.assertEqual(u1.followers.all(), [])

        u1.follow(u2)
        db.session.commit()
        self.assertTrue(u1.is_following(u2))
        self.assertEqual(u1.followed.count(), 1)
        self.assertEqual(u1.followed.first().username, 'susan')
        self.assertEqual(u2.followers.count(), 1)
        self.assertEqual(u2.followers.first().username, 'john')

        u1.unfollow(u2)
        db.session.commit()
        self.assertFalse(u1.is_following(u2))
        self.assertEqual(u1.followed.count(), 0)
        self.assertEqual(u2.followers.count(), 0)

    def test_follow_songs(self):
        u1 = User(username='john')
        u2 = User(username='susan')
        u3 = User(username='mary')
        u4 = User(username='david')
        db.session.add_all([u1, u2, u3, u4])

        # create 4 Songs
        now = datetime.utcnow()
        p1 = Song(song_name="Song from john", contributer=u1, timestamp=now + timedelta(seconds=1))
        p2 = Song(song_name="Song from susan", contributer=u2, timestamp=now + timedelta(seconds=4))
        p3 = Song(song_name="Song from mary", contributer=u3, timestamp=now + timedelta(seconds=3))
        p4 = Song(song_name="Song from david", contributer=u4, timestamp=now + timedelta(seconds=2))
        db.session.add_all([p1, p2, p3, p4])
        db.session.commit()

        # setup the followers
        u1.follow(u2)
        u1.follow(u4)
        u2.follow(u3)
        u3.follow(u4)
        db.session.commit()

        # check the followed song of each user
        f1 = u1.followed_songs().all()
        f2 = u2.followed_songs().all()
        f3 = u3.followed_songs().all()
        f4 = u4.followed_songs().all()
        self.assertEqual(f1, [p2, p4, p1])
        self.assertEqual(f2, [p2, p3])
        self.assertEqual(f3, [p3, p4])
        self.assertEqual(f4, [p4])

if __name__ == '__main__':
    unittest.main(verbosity=2)


