from model import TweetDao, UserDao
import pytest
from sqlalchemy import create_engine, text
import config
import bcrypt

database = create_engine(
    config.test_config['DB_URL'], encoding='utf-8', max_overflow=0)


@pytest.fixture
def user_dao():
    return UserDao(database)


@pytest.fixture
def tweet_dao():
    return TweetDao(database)


def setup_function():
    users = [{'name': 'GilGeuno',
              'email': 'rlfrmsdh@nextlab.co.kr',
              'password': 'wlrkq159',
              'profile': 'Developer'},
             {'name': 'GongDeok',
              'email': 'GongDeok@google.com',
              'password': 'kil159',
              'profile': 'station'}]

    users[0]['password'] = bcrypt.hashpw(
        users[0]['password'].encode('UTF-8'), bcrypt.gensalt())
    users[1]['password'] = bcrypt.hashpw(
        users[1]['password'].encode('UTF-8'), bcrypt.gensalt())

    database.execute(text(
        """INSERT INTO users (name, email, hashed_password, profile) VALUES (:name, :email, :password, :profile)"""), users)
    tweet = {'user_id': 2, 'tweet': 'Hello~'}
    database.execute(
        text("""INSERT INTO tweets (user_id, tweet) VALUES (:user_id, :tweet)"""), tweet)


def teardown_function():
    database.execute(text("SET FOREIGN_KEY_CHECKS=0"))
    database.execute(text("TRUNCATE users"))
    database.execute(text("TRUNCATE users_follow_list"))
    database.execute(text("TRUNCATE tweets"))
    database.execute(text("SET FOREIGN_KEY_CHECKS=1"))


# tweet_dao.py
def test_get_tweets(tweet_dao):
    tweet = tweet_dao.get_tweets([2])
    assert tweet[0]['user_id'] == 2 and tweet[0]['tweet'] == 'Hello~'


def test_insert_tweet(tweet_dao):
    user_tweet = {'id': 1, 'tweet': 'test'}
    tweet_dao.insert_tweet(user_tweet)
    tweet = tweet_dao.get_tweets([1])
    assert tweet[0]['user_id'] == 1 and tweet[0]['tweet'] == 'test'


def test_get_follow_ids(tweet_dao):
    follow_ids = tweet_dao.get_follow_ids(1)
    assert follow_ids == []
    database.execute(text(
        """INSERT INTO users_follow_list (user_id, follow_user_id) VALUES (1, 2)"""))
    follow_ids = tweet_dao.get_follow_ids(1)
    assert follow_ids == [2]


def test_insert_follow_unfollow(user_dao, tweet_dao):
    user_follow = {'id': 1, 'follow': 2}
    user_dao.insert_follow(user_follow)
    follow_ids = tweet_dao.get_follow_ids(1)
    assert follow_ids == [2]
    user_unfollow = {'id': 1, 'unfollow': 2}
    user_dao.insert_unfollow(user_unfollow)
    follow_ids = tweet_dao.get_follow_ids(1)
    assert follow_ids == []


# user_dao.py
def test_read_user_info(user_dao):
    user_info = user_dao.read_user_info(1)
    assert user_info == {'id': 1, 'name': 'GilGeuno', 'email': 'rlfrmsdh@nextlab.co.kr',
                         'profile': 'Developer'}


def test_insert_user(user_dao):
    hashed_password = bcrypt.hashpw(
        'kil159'.encode('UTF-8'), bcrypt.gensalt())
    user_info = {'name': 'GalGal', 'email': 'Gal@gmail.com',
                 'profile': 'Garbage',
                 'password': hashed_password}
    user_dao.insert_user(user_info)
    new_user = user_dao.read_user_info(3)
    assert new_user == {'id': 3, 'name': 'GalGal', 'email': 'Gal@gmail.com',
                        'profile': 'Garbage'}


def test_get_user_id_pw(user_dao):
    email = 'rlfrmsdh@nextlab.co.kr'
    user_id_pw = user_dao.get_user_id_pw(email)
    assert user_id_pw['id'] == 1
    assert bcrypt.checkpw('wlrkq159'.encode('utf-8'),
                          user_id_pw['hashed_password'].encode('utf-8'))


def test_get_all_user_id(user_dao):
    ids = user_dao.get_all_user_id()
    ids.sort()
    assert ids == [1, 2]


def test_get_all_users(user_dao):
    users = user_dao.get_all_users()
    assert users['1'] == ('GilGeuno', 'rlfrmsdh@nextlab.co.kr', 'Developer')
    assert users['2'] == ('GongDeok', 'GongDeok@google.com', 'station')


def test_picture_path_save(user_dao):
    user_dao.picture_path_save(1, 'test_path')
    row = database.execute(
        text(f"""SELECT profile_picture FROM users WHERE id= 1""")).fetchone()
    assert row['profile_picture'] == 'test_path'


def test_get_pic_path(user_dao):
    user_dao.picture_path_save(1, 'test_path')
    path = user_dao.get_pic_path(1)
    assert path == 'test_path'


# if __name__ == "__main__":
#     userDao = user_dao()
#     test_picture_path_save(userDao)
