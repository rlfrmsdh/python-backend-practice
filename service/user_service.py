import bcrypt
import jwt
import os
from datetime import datetime, timedelta
import boto3


class UserService():
    def __init__(self, user_dao, config):
        self.user_dao = user_dao
        self.config = config
        self.s3 = boto3.client("s3", aws_access_key_id=config['S3_ACCESS_KEY'],
                               aws_secret_access_key=config['S3_SECRET_KEY'])

    def create_new_user(self, user):
        user['password'] = bcrypt.hashpw(
            user['password'].encode('UTF-8'), bcrypt.gensalt())
        return self.user_dao.insert_user(user)

    def get_user_by_id(self, user_id):
        return self.user_dao.read_user_info(user_id)

    def get_user_id_pw_by_email(self, email):
        return self.user_dao.get_user_id_pw(email)

    def login_check(self, credential):
        email = credential['email']
        password = credential['password']
        user_info = self.user_dao.get_user_id_pw(email)
        if user_info and bcrypt.checkpw(password.encode('UTF-8'), user_info['hashed_password'].encode('UTF-8')):
            return True
        else:
            return False

    def generate_tokens(self, user):
        user_id = user['id']
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)
        }
        token = jwt.encode(payload, self.config['JWT_SECRET_KEY'], 'HS256')
        return {'access_token': token.decode('UTF-8')}

    def enrolled_user_check(self, user_id):
        registered_ids = self.user_dao.get_all_user_id()

        if user_id in registered_ids:
            return True
        else:
            return False

    def follow_user(self, user_id, follow_id):
        user_follow = {'id': user_id, 'follow': follow_id}
        return self.user_dao.insert_follow(user_follow)

    def unfollow_user(self, user_id, unfollow_id):
        user_unfollow = {'id': user_id, 'unfollow': unfollow_id}
        return self.user_dao.insert_unfollow(user_unfollow)

    def show_user_list(self):
        return self.user_dao.get_all_users()

    def profile_pic_save(self, picture, filename, user_id):
        self.s3.upload_fileobj(picture, self.config['S3_BUCKET'], filename)
        image_url = f"{self.config['S3_BUCKET_URL']}{filename}"
        return self.user_dao.picture_path_save(user_id, image_url)

    def get_prof_pic_url(self, user_id):
        return self.user_dao.get_pic_path(user_id)
