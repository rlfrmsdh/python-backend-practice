import config
from sqlalchemy import create_engine, text
import pytest
from app import create_app
import bcrypt
import json
import io
from unittest import mock
database = create_engine(
    config.test_config['DB_URL'], encoding='UTF-8', max_overflow=0)


@pytest.fixture
@mock.patch("service.user_service.boto3")
def api(mock_boto3):
    mock_boto3.client.return_value = mock.Mock()
    app = create_app(config.test_config)
    app.config['TEST'] = True
    api = app.test_client()
    return api


def setup_function():
    password = 'wlrkq159'
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    users = [{'name': 'GilGeuno',
              'email': 'rlfrmsdh@nextlab.co.kr',
              'profile': 'Developer',
              'hashed_password': hashed_password},
             {'name': 'MrLee',
              'email': 'easylee@nextlab.co.kr',
              'profile': 'cleaner',
              'hashed_password': hashed_password}]
    database.execute(text("""INSERT INTO users (name, email, profile, hashed_password)
                            VALUES (:name, :email, :profile, :hashed_password)"""), users)
    database.execute(
        text("""INSERT INTO tweets (user_id, tweet) VALUES (2, "Hello World")"""))


def teardown_function():
    database.execute(text("SET FOREIGN_KEY_CHECKS=0"))
    database.execute(text("TRUNCATE users"))
    database.execute(text("TRUNCATE users_follow_list"))
    database.execute(text("TRUNCATE tweets"))
    database.execute(text("SET FOREIGN_KEY_CHECKS=1"))


def test_ping(api):
    result = api.get("/ping")
    assert b'pong' in result.data


def test_login(api):
    resp = api.post("/login",
                    data=json.dumps(
                        {"email": "rlfrmsdh@nextlab.co.kr", "password": "wlrkq159"}),
                    content_type='application/json')
    assert b'access_token' in resp.data
    # token = json.loads(resp.data.decode('utf-8'))
    # assert token['access_token']


def test_unauthorized(api):
    ret = api.post("/tweet", data=json.dumps({"tweet": "Hoollly~~"}),
                   content_type='application/json')
    assert ret.status_code == 401

    ret = api.post("/follow", data=json.dumps({"follow": 2}),
                   content_type='application/json')
    assert ret.status_code == 401

    ret = api.post("/unfollow", data=json.dumps({'unfollow': 2}),
                   content_type='application/json')
    assert ret.status_code == 401


def test_follow(api):
    resp = api.post("/login",
                    data=json.dumps(
                        {"email": "rlfrmsdh@nextlab.co.kr", "password": "wlrkq159"}),
                    content_type='application/json')
    token = json.loads(resp.data.decode('utf-8'))
    assert b"access_token" in resp.data

    tweets = api.get("/timeline/1")
    tweets = json.loads(tweets.data.decode('utf-8'))
    assert tweets['user_id'] == 1
    assert tweets['timeline'] == []

    ret = api.post("/follow", data=json.dumps({"follow": 2}),
                   content_type='application/json',
                   headers={'Authorization': token['access_token']})
    assert ret.status_code == 200
    tweets = api.get("/timeline/1")
    tweets = json.loads(tweets.data.decode('utf-8'))
    assert tweets['user_id'] == 1
    assert tweets['timeline'] == [{'user_id': 2, 'tweet': "Hello World"}]


def test_unfollow(api):
    resp = api.post("/login",
                    data=json.dumps(
                        {"email": "rlfrmsdh@nextlab.co.kr", "password": "wlrkq159"}),
                    content_type='application/json')
    token = json.loads(resp.data.decode('utf-8'))
    assert b"access_token" in resp.data

    ret = api.post("/follow", data=json.dumps({"follow": 2}),
                   content_type='application/json',
                   headers={'Authorization': token['access_token']})
    assert ret.status_code == 200

    tweets = api.get("/timeline/1")
    tweets = json.loads(tweets.data.decode('utf-8'))
    assert tweets['user_id'] == 1
    assert tweets['timeline'] == [{'user_id': 2, 'tweet': "Hello World"}]

    ret = api.post("/unfollow", data=json.dumps({"unfollow": 2}),
                   content_type='application/json',
                   headers={'Authorization': token['access_token']})
    assert ret.status_code == 200

    tweets = api.get("/timeline/1")
    tweets = json.loads(tweets.data.decode('utf-8'))

    assert tweets['user_id'] == 1
    assert tweets['timeline'] == []


def test_tweet(api):
    resp = api.post("/login",
                    data=json.dumps(
                        {"email": "rlfrmsdh@nextlab.co.kr", "password": "wlrkq159"}),
                    content_type='application/json')
    token = json.loads(resp.data.decode('utf-8'))
    # print(token)
    assert token.get('access_token')
    # rows = database.execute(text("""SELECT * FROM users"""))

    ret = api.post("/tweet", data=json.dumps({"tweet": "Hoollly~~"}),
                   content_type='application/json',
                   headers={'Authorization': token['access_token']})
    assert ret.status_code == 200

    tweets = api.get("/timeline/1")
    # print(tweets)
    tweets_data = json.loads(tweets.data.decode('utf-8'))
    assert tweets_data['user_id'] == 1
    assert tweets_data['timeline'] == [{"user_id": 1,
                                        "tweet": "Hoollly~~"}]


def test_upload_profile_picture(api):
    resp = api.post("/login",
                    data=json.dumps(
                        {"email": "rlfrmsdh@nextlab.co.kr", "password": "wlrkq159"}),
                    content_type="application/json")
    token = json.loads(resp.data.decode('utf-8'))
    assert token.get('access_token')

    ret = api.get("/profile-picture/1")
    # img_url = json.loads(ret.data.decode('utf-8'))
    assert ret.data.decode('utf-8') is ''

    resp = api.post("/profile-picture",
                    content_type='multipart/form-data',
                    headers={'Authorization': token['access_token']},
                    data={"profile_pic": (io.BytesIO(b'some image here'), 'profile.png')})
    assert resp.status_code == 200

    ret = api.get("/profile-picture/1")
    img_url = json.loads(ret.data.decode('utf-8'))
    assert img_url['img_url'] == "https://s3.ap-northeast-2.amazonaws.com/python-backend-miniter-test/profile.png"
