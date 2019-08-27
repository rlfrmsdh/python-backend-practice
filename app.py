from flask import Flask, request, jsonify, current_app, Response, g
from flask_cors import CORS
from flask.json import JSONEncoder
from sqlalchemy import create_engine, text
import bcrypt
import datetime
import jwt
import functools


def login_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        access_token = request.headers.get('Authorization')
        if access_token is not None:
            try:
                payload = jwt.decode(
                    access_token, current_app.config['JWT_SECRET_KEY'], 'HS256')
            except jwt.InvalidTokenError:
                payload = None
            if payload is None:
                return Response(response='invalid token', status=401)

            user_id = payload['user_id']
            g.user_id = user_id
            g.user = get_user_info(user_id)
        else:
            return Response(response='Not authorized', status=401)
        return f(*args, **kwargs)
    return decorated_function


def get_user_info(user_id):
    user = current_app.database.execute(text(
        """SELECT id, name, email, profile FROM users WHERE id = :user_id"""), {'user_id': user_id}).fetchone()
    return {'id': user['id'], 'name': user['name'], 'email': user['email'], 'profile': user['profile']} if user else None


def insert_follow(user_follow):
    return current_app.database.execute(text("""INSERT INTO users_follow_list (user_id, follow_user_id) VALUES (:id, :follow)"""), user_follow).rowcount


def insert_unfollow(user_unfollow):
    return current_app.database.execute(text("""DELETE FROM users_follow_list WHERE user_id= :id AND follow_user_id = :unfollow"""), user_unfollow).rowcount


def insert_tweet(user_tweet):
    return current_app.database.execute(text("""INSERT INTO tweets (user_id, tweet) VALUES (:id, :tweet)"""), user_tweet).rowcount


def get_timeline(user_id):
    follow_ids = current_app.database.execute(
        text("""SELECT follow_user_id FROM users_follow_list where user_id= :user_id"""), user_id).fetchall()
    exist_ids = [str(x) for (x,) in follow_ids] + [str(user_id['user_id'])]
    exist_ids = ','.join(exist_ids)

    tweets = current_app.database.execute(
        text(f"""SELECT tweet, user_id FROM tweets WHERE user_id in ({exist_ids})""")).fetchall()

    return [{"user_id": tweet['user_id'], "tweet": tweet['tweet']}
            for tweet in tweets]


def create_app(test_config=None):
    app = Flask(__name__)
    CORS(app)
    if test_config is None:
        app.config.from_pyfile('config.py')
    else:
        app.config.update(test_config)

    database = create_engine(
        app.config['DB_URL'], encoding='utf-8', max_overflow=0)
    app.database = database

    @app.route("/ping", methods=['GET'])
    def ping():
        return "pong"

    @app.route("/sign-up", methods=['POST'])
    def sign_up():
        new_user = request.json
        new_user['password'] = bcrypt.hashpw(
            new_user['password'].encode('UTF-8'), bcrypt.gensalt())
        new_user_id = app.database.execute(text("""INSERT INTO users(
            name,
            email,
            profile,
            hashed_password) VALUES (
                :name,
                :email,
                :profile,
                :password
            )
            """), new_user).lastrowid
        row = app.database.execute(text("""SELECT
            id,
            name,
            email,
            profile
        FROM users
        WHERE id = :user_id"""), {'user_id': new_user_id}).fetchone()
        created_user = {
            'id': row['id'],
            'name': row['name'],
            'email': row['email'],
            'profile': row['profile']} if row else None

        return jsonify(created_user)

    @app.route("/login", methods=['POST'])
    def login():
        inputs = request.json
        email = inputs['email']
        password = inputs['password']
        row = app.database.execute(text("""SELECT id, hashed_password FROM users WHERE email= :email"""), {
                                   'email': email}).fetchone()
        if row and bcrypt.checkpw(password.encode('UTF-8'), row['hashed_password'].encode('UTF-8')):
            user_id = row['id']
            payload = {
                'user_id': user_id,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=60 * 60 * 24)
            }
            token = jwt.encode(payload, app.config['JWT_SECRET_KEY'], 'HS256')
            return jsonify({'access_token': token.decode('UTF-8')})
        else:
            return '', 401

    @app.route("/tweet", methods=['POST'])
    @login_required
    def tweet():
        user_tweet = request.json
        tweet = user_tweet['tweet']
        user_tweet['id'] = g.user_id

        if len(tweet) >= 300:
            return 'exceed 300 characters', 400

        insert_tweet(user_tweet)

        return '', 200

    @app.route("/timeline/<int:user_id>", methods=['GET'])
    def timeline(user_id):
        registered_ids = app.database.execute(
            text("""SELECT id from users""")).fetchall()
        registered_ids = [x for (x,) in registered_ids]
        user_info = {"user_id": user_id}
        if user_id not in registered_ids:
            return '사용자 존재x ', 400

        timeline = {'user_id': user_id,
                    'timeline': get_timeline(user_info)}

        return jsonify(timeline), 200

    @app.route("/timeline", methods=['GET'])
    @login_required
    def user_timeline():
        user_id = g.user_id
        registered_ids = app.database.execute(
            text("""SELECT id from users""")).fetchall()
        registered_ids = [x for (x,) in registered_ids]
        user_info = {"user_id": user_id}
        if user_id not in registered_ids:
            return '사용자 존재x ', 400

        return jsonify(get_timeline(user_info)), 200

    @app.route("/follow", methods=['POST'])
    @login_required
    def follow():
        payload = request.json
        payload['id'] = g.user_id

        ids = app.database.execute(text("""SELECT id FROM users""")).fetchall()
        ids = [x for (x,) in ids]
        if g.user_id not in ids or int(payload['follow']) not in ids:
            return "ID does not exist(id or follow id)", 400
        print(insert_follow(payload))
        return '', 200

    @app.route("/unfollow", methods=['POST'])
    @login_required
    def unfollow():
        payload = request.json
        payload['id'] = g.user_id

        ids = app.database.execute(text("""SELECT id FROM users""")).fetchall()
        ids = [x for (x,) in ids]
        if g.user_id not in ids or int(payload['unfollow']) not in ids:
            return "ID does not exist(id or follow id)", 400
        print(insert_unfollow(payload))

        return '', 200

    @app.route("/user-list", methods=['GET'])
    def show_user_list():
        rows = app.database.execute(text("""SELECT * from users""")).fetchall()
        data = {}
        for row in rows:
            data[row['id']] = (row['name'], row['email'], row['profile'])

        return jsonify(data)
    return app


"""app.id_count = 1
app.users = {}

    

class CustomJsonEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return JSONEncoder.default(self, obj)


app.json_encoder = CustomJsonEncoder





app.tweet = []





"""
