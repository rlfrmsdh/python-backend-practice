from sqlalchemy import text, create_engine


class TweetDao():
    def __init__(self, database):
        self.db = database

    def insert_tweet(self, user_tweet):
        return self.db.execute(text("""INSERT INTO tweets (user_id, tweet) VALUES (:id, :tweet)"""), user_tweet).rowcount

    def get_follow_ids(self, user_id):
        follow_ids = self.db.execute(
            text("""SELECT follow_user_id FROM users_follow_list where user_id= :user_id"""), user_id).fetchall()
        follow_ids = [str(x) for (x,) in follow_ids]
        return follow_ids

    def get_tweets(self, ids):
        tweets = self.db.execute(
            text(f"""SELECT tweet, user_id FROM tweets WHERE user_id in ({ids})""")).fetchall()
        return tweets


# if __name__ == "__main__":
#     db = {
#         'user': 'root',
#         'password': 'wlrkq159',
#         'host': 'localhost',
#         'port': 3306,
#         'database': 'miniter'
#     }
#     DB_URL = f"mysql+mysqlconnector://{db['user']}:{db['password']}@{db['host']}:{db['port']}/{db['database']}?charset=utf8"

#     database = create_engine(DB_URL)
#     tweet_dao = TweetDao(database)
#     user_tweet = {'id': 3, 'tweet': 'test'}
#     ret = tweet_dao.insert_tweet(user_tweet)
#     print(ret)
