from service import UserService, TweetService
from model import TweetDao, UserDao
import pytest
from sqlalchemy import create_engine, text
import config
import bcrypt

database = create_engine(
    config.test_config['DB_URL'], encoding='utf-8', max_overflow=0)


@pytest.fixture
def user_service():
    userDao = UserDao(database)
    return UserService(userDao, config.test_config)


@pytest.fixture
def tweet_service():
    tweetDao = TweetDao(database)
    return TweetService(tweetDao)


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
def test_get_user_by_id(user_service):
    user = user_service.get_user_by_id(1)
    assert user['id'] == 1 and user['name'] == 'GilGeuno'\
        and user['email'] == 'rlfrmsdh@nextlab.co.kr' and user['profile'] == 'Developer'


def test_create_new_user(user_service):

    new_user = {'name': 'Gil', 'email': 'gil@gmail.com', 'profile': 'Developer',
                'password': 'kil159'}
    user_service.create_new_user(new_user)
    new_user_info = user_service.get_user_by_id(3)
    assert new_user_info['id'] == 3 and new_user_info['name'] == 'Gil' and\
        new_user_info['profile'] == 'Developer' and new_user_info['email'] == 'gil@gmail.com'
