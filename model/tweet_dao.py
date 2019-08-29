from sqlalchemy import text, create_engine


class TweetDao():
    def __init__(self, database):
        self.db = database

    def insert_tweet(self, user_tweet):
        return self.db.execute(text("""INSERT INTO tweets (user_id, tweet) VALUES (:id, :tweet)"""), user_tweet).rowcount

    def get_follow_ids(self, user_id):

        follow_ids = self.db.execute(
            text(f"""SELECT follow_user_id FROM users_follow_list where user_id= {user_id}""")).fetchall()
        follow_ids = [x for (x,) in follow_ids]
        return follow_ids

    def get_tweets(self, ids: list):
        ids = [str(id) for id in ids]
        ids = ','.join(ids)

        tweets = self.db.execute(
            text(f"""SELECT tweet, user_id FROM tweets WHERE user_id in ({ids})""")).fetchall()
        return tweets
