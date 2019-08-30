from flask import request, jsonify, current_app, Response, g, send_file
from flask.json import JSONEncoder
from werkzeug.utils import secure_filename
import bcrypt
import jwt
import functools

from service import UserService, TweetService
from model import UserDao, TweetDao


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
        else:
            return Response(response='Not authorized', status=401)
        return f(*args, **kwargs)
    return decorated_function


def create_endpoints(app, services):
    user_service = services.user_service
    tweet_service = services.tweet_service

    @app.route("/ping", methods=['GET'])
    def ping():
        return "pong"

    @app.route("/sign-up", methods=['POST'])
    def sign_up():
        new_user = request.json
        new_user_id = user_service.create_new_user(new_user)
        created_user = user_service.get_user_by_id(new_user_id)
        # return jsonify(created_user)
        return Response(jsonify(created_user), 200)

    @app.route("/login", methods=['POST'])
    def login():
        credential = request.json
        authorized = user_service.login_check(credential)

        if authorized:
            user = user_service.get_user_id_pw_by_email(credential['email'])
            token = user_service.generate_tokens(user)
            return jsonify(token)
        else:
            return '', 401

    @app.route("/profile-picture", methods=['POST'])
    @login_required
    def upload_profile_picture():
        user_id = g.user_id
        if 'profile_pic' not in request.files:

            return 'File is missing', 401
        profile_pic = request.files['profile_pic']

        if profile_pic.filename == '':
            return 'File is missing', 401
        print("request.files : ", request.files)
        filename = secure_filename(profile_pic.filename)
        user_service.profile_pic_save(profile_pic, filename, user_id)

        return '', 200

    @app.route("/profile-picture/<int:user_id>", methods=['GET'])
    def download_profile_picture(user_id):
        img_path = user_service.get_prof_pic_url(user_id)

        if img_path:
            return jsonify({'img_url': img_path})
        else:
            return '', 404

    @app.route("/tweet", methods=['POST'])  # tweet
    @login_required
    def tweet():
        user_tweet = request.json
        user_tweet['id'] = g.user_id

        ret = tweet_service.tweet(user_tweet)
        if ret:
            return '', 200
        else:
            return 'exceed 300 characters', 401

    @app.route("/timeline/<int:user_id>", methods=['GET'])
    def timeline(user_id):
        enrolled = user_service.enrolled_user_check(user_id)
        if not enrolled:
            return '사용자 존재x ', 400

        timeline = {'user_id': user_id,
                    'timeline': tweet_service.get_timeline(user_id)}

        return jsonify(timeline), 200

    @app.route("/timeline", methods=['GET'])
    @login_required
    def user_timeline():
        user_id = g.user_id
        enrolled = user_service.enrolled_user_check(user_id)
        if not enrolled:
            return '사용자 존재x ', 400

        timeline = {'user_id': user_id,
                    'timeline': tweet_service.get_timeline(user_id)}

        return jsonify(timeline), 200

    @app.route("/follow", methods=['POST'])
    @login_required
    def follow():
        payload = request.json
        payload['id'] = g.user_id
        enrolled_id = user_service.enrolled_user_check(payload['id'])
        enrolled_follow = user_service.enrolled_user_check(payload['follow'])
        if not enrolled_id or not enrolled_follow:
            return "ID does not exist(id or follow id)", 400
        user_service.follow_user(payload['id'], payload['follow'])
        return '', 200

    @app.route("/unfollow", methods=['POST'])
    @login_required
    def unfollow():
        payload = request.json
        payload['id'] = g.user_id
        enrolled_id = user_service.enrolled_user_check(payload['id'])
        enrolled_unfol = user_service.enrolled_user_check(payload['unfollow'])
        if not enrolled_id or not enrolled_unfol:
            return "ID does not exist(id or follow id)", 400
        user_service.unfollow_user(payload['id'], payload['unfollow'])
        return '', 200

    @app.route("/user-list", methods=['GET'])
    def show_user_list():
        return jsonify(user_service.show_user_list())
