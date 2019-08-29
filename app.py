from flask import Flask
from flask_cors import CORS
from sqlalchemy import create_engine
from service import UserService, TweetService
from model import UserDao, TweetDao
from view import create_endpoints


class Service():
    pass


def create_app(test_config=None):
    app = Flask(__name__)
    CORS(app)

    if test_config is None:
        app.config.from_pyfile("config.py")
    else:
        app.config.update(test_config)

    database = create_engine(
        app.config['DB_URL'], encoding='UTF-8', max_overflow=0)

    userDao = UserDao(database)
    tweetDao = TweetDao(database)

    service = Service()
    service.tweetService = TweetService(tweetDao)
    service.userService = UserService(userDao, app.config)

    create_endpoints(app, service)

    return app
