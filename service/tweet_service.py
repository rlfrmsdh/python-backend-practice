

class TweetService():
    def __init__(self, tweet_dao):
        self.tweet_dao = tweet_dao

    def tweet(self, user_tweet):
        if len(user_tweet['tweet']) >= 300:
            return None

        return self.tweet_dao.insert_tweet(user_tweet)

    def get_timeline(self, user_id):

        follow_ids = self.tweet_dao.get_follow_ids(user_id)
        exist_ids = follow_ids + [str(user_id)]
        exist_ids = ','.join(exist_ids)

        tweets = self.tweet_dao.get_tweets(exist_ids)

        return [{"user_id": tweet['user_id'], "tweet": tweet['tweet']}
                for tweet in tweets]
