from sqlalchemy import text


class UserDao():
    def __init__(self, database):
        self.db = database

    def insert_user(self, user):
        new_user_id = self.db.execute(text("""INSERT INTO users(
            name,
            email,
            profile,
            hashed_password) VALUES (
                :name,
                :email,
                :profile,
                :password
            )
            """), user).lastrowid
        return new_user_id

    def read_user_info(self, user_id):
        user = self.db.execute(text(
            """SELECT id, name, email, profile FROM users WHERE id = :user_id"""), {'user_id': user_id}).fetchone()
        return {'id': user['id'], 'name': user['name'], 'email': user['email'], 'profile': user['profile']} if user else None

    def get_user_id_pw(self, email):
        row = self.db.execute(text("""SELECT id, hashed_password FROM users WHERE email= :email"""), {
            'email': email}).fetchone()
        return row

    def get_all_user_id(self):
        registered_ids = self.db.execute(
            text("""SELECT id from users""")).fetchall()
        registered_ids = [x for (x,) in registered_ids]
        return registered_ids

    def insert_follow(self, user_follow):
        return self.db.execute(text("""INSERT INTO users_follow_list (user_id, follow_user_id) VALUES (:id, :follow)"""), user_follow).rowcount

    def insert_unfollow(self, user_unfollow):
        return self.db.execute(text("""DELETE FROM users_follow_list WHERE user_id= :id AND follow_user_id = :unfollow"""), user_unfollow).rowcount

    def get_all_users(self):
        rows = self.db.execute(text("""SELECT * from users""")).fetchall()
        data = {}
        for row in rows:
            data[f"{row['id']}"] = (row['name'], row['email'], row['profile'])
        return data

    def picture_path_save(self, user_id, path):
        return self.db.execute(text("""UPDATE users SET profile_picture= :path WHERE id = :user_id"""), {'path': path, 'user_id': user_id}).rowcount

    def get_pic_path(self, user_id):
        row = self.db.execute(
            text(f"""SELECT profile_picture FROM users WHERE id = {user_id}""")).fetchone()
        return row['profile_picture'] if row else None
