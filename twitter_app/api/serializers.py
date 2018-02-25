from rest_framework import serializers
from api.models import Tweet

class TweetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tweet
        fields = ("tweet_id", "text", "truncated", "lang", "user_id", "user_screen_name", "user_name", "user_verified",  "user_location", "created_at", "user_utc_offset", "user_time_zone", "favorite_count", "retweet_count", "user_followers_count", "user_friends_count")
