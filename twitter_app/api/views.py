from rest_framework import viewsets, status
from rest_framework.decorators import list_route, detail_route
from rest_framework.response import Response

import twitter
import time
import json
import datetime
import dateutil.parser
from django.utils import timezone
from django.utils.timezone import is_aware, make_aware
import csv

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

from api.models import Tweet
from api.serializers import TweetSerializer

import os.path

consumer_key = 'c2nYMVrtOx74TOHoBO0AMlVfF'
consumer_secret = 'otQ4DVFxvDE2uglw7pT1GVR5ShhTaE2SaSd6e5b715xdapX7G6'
access_token_key = '1435400665-p1B4y1FfuHnIpSDB5v3kDQy4YUx6JD3oy807H0C'
access_token_secret = 'aNMjiTd6ulsjAjDIOT71R7ZlaynTJc7YzMLuHYQgAPnzo'

all_tweets = []
current_timezone = timezone.get_current_timezone()

class Twitter(viewsets.ViewSet):

    def esport_to_csv(self, tweets, file_name, delete_existing):
        if delete_existing == "true" and os.path.exists(file_name):
            os.remove(file_name)
        with open(file_name, 'w') as new_file:
            fieldnames = ["tweet_id", "text" , "user_screen_name", "user_name", "user_verified",
                          "created_at", "user_time_zone", "user_location", "favorite_count",
                          "retweet_count", "user_followers_count", "user_friends_count"]
            csv_writer = csv.DictWriter(new_file, fieldnames=fieldnames, extrasaction='ignore', delimiter='\t')
            csv_writer.writeheader()
            for tweet in tweets:
                csv_writer.writerow(tweet)
        if delete_existing == "false":
            with open(file_name, 'w') as csv_file:
                fieldnames = ["tweet_id", "text", "user_screen_name", "user_name", "user_verified",
                              "created_at","user_time_zone", "user_location", "favorite_count",
                              "retweet_count","user_followers_count", "user_friends_count"]
                csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames, extrasaction='ignore', delimiter='\t')
                csv_writer.writeheader()
                for tweet in tweets:
                    csv_writer.writerow(tweet)



    @list_route(methods=['post'])
    def stream(self, request):
        global all_tweets
        response = {}
        keywords = request.POST.get("keywords", "none").split(',')
        print(keywords, type(keywords))
        timeout = request.POST.get("timeout", 2)
        if keywords[0] != "none":
            auth = OAuthHandler(consumer_key, consumer_secret)
            auth.set_access_token(access_token_key, access_token_secret)
            mystream = Stream(auth=auth, listener=mystreamListener(time_limit=int(timeout)))
            mystream.filter(track=keywords)

            print(len(all_tweets))
            l = 0
            for tweet in all_tweets: #ignoring repeating tweets
                try:
                    ae_tweet = Tweet.objects.get(tweet_id=tweet["id"])
                    l = l + 1
                    print("tweet repeated")
                except Exception:
                    ae_tweet = None
                if ae_tweet is None:
                    Tweet.create_from_json(tweet)

            response["message"] = "out of " + str(len(all_tweets)) + " tweets streamed, " + str(
                l) + " are duplicate hence " + str(len(all_tweets) - l) + " tweets are added to the database"

            return Response(response, status=status.HTTP_200_OK)

        response["message"] = "not done"
        return Response(response, status=status.HTTP_200_OK)

    @list_route(methods=["post"])
    def get_created_in_range(self, request):
        response = {}

        data = request.POST
        start = dateutil.parser.parse(data['start'])
        end = dateutil.parser.parse(data['end'])
        page_no = data['page_no']
        export_to_csv = data.get('export_to_csv', "false")
        delete_existing = data.get('delete_existing', "false")
        file_name = data.get('csv_file_name', "none")

        tweets = Tweet.get_created_in_range(start, end, int(page_no))
        serializer = TweetSerializer(tweets, many= True)
        if export_to_csv == "true" and file_name != "none":
            self.esport_to_csv(serializer.data, file_name, delete_existing)

        response["data"] = serializer.data
        return Response(response, status= status.HTTP_200_OK)

    @list_route(methods=["post"])
    def filter_retweet_count(self, request):
        response = {}
        data = request.POST
        page_no = data['page_no']
        export_to_csv = data.get('export_to_csv', "false")
        delete_existing = data.get('delete_existing', "false")
        file_name = data.get('csv_file_name', "none")

        tweets = Tweet.filter_retweet_count(data["type"], data["retweet_count"], int(page_no))
        serializer = TweetSerializer(tweets, many=True)
        if export_to_csv == "true" and file_name != "none":
            self.esport_to_csv(serializer.data, file_name, delete_existing)

        response["data"] = serializer.data
        return Response(response, status=status.HTTP_200_OK)

    @list_route(methods=["post"])
    def filter_favorite_count(self, request):
        response = {}
        data = request.POST
        page_no = data['page_no']
        export_to_csv = data.get('export_to_csv', "false")
        delete_existing = data.get('delete_existing', "false")
        file_name = data.get('csv_file_name', "none")

        tweets = Tweet.filter_favorite_count(data["type"], data["favorite_count"], int(page_no))
        serializer = TweetSerializer(tweets, many=True)
        if export_to_csv == "true" and file_name != "none":
            self.esport_to_csv(serializer.data, file_name, delete_existing)

        response["data"] = serializer.data
        return Response(response, status=status.HTTP_200_OK)

    @list_route(methods=["post"])
    def filter_screen_name(self, request):
        response = {}
        data = request.POST
        page_no = data['page_no']
        export_to_csv = data.get('export_to_csv', "false")
        delete_existing = data.get('delete_existing', "false")
        file_name = data.get('csv_file_name', "none")

        tweets = Tweet.filter_screen_name(data["type"], data["screen_name"], int(page_no))
        serializer = TweetSerializer(tweets, many=True)
        if export_to_csv == "true" and file_name != "none":
            self.esport_to_csv(serializer.data, file_name, delete_existing)

        response["data"] = serializer.data
        return Response(response, status=status.HTTP_200_OK)

    @list_route(methods=["post"])
    def filter_user_name(self, request):
        response = {}
        data = request.POST
        page_no = data['page_no']
        export_to_csv = data.get('export_to_csv', "false")
        delete_existing = data.get('delete_existing', "false")
        file_name = data.get('csv_file_name', "none")

        tweets = Tweet.filter_user_name(data["type"], data["user_name"], int(page_no))
        serializer = TweetSerializer(tweets, many=True)
        if export_to_csv == "true" and file_name != "none":
            self.esport_to_csv(serializer.data, file_name, delete_existing)

        response["data"] = serializer.data
        return Response(response, status=status.HTTP_200_OK)

    @list_route(methods=["post"])
    def filter_text(self, request):
        response = {}
        data = request.POST
        page_no = data['page_no']
        export_to_csv = data.get('export_to_csv', "false")
        delete_existing = data.get('delete_existing', "false")
        file_name = data.get('csv_file_name', "none")

        tweets = Tweet.filter_text(data["type"], data["text"], int(page_no))
        serializer = TweetSerializer(tweets, many=True)
        if export_to_csv == "true" and file_name != "none":
            self.esport_to_csv(serializer.data, file_name, delete_existing)

        response["data"] = serializer.data
        return Response(response, status=status.HTTP_200_OK)


class mystreamListener(StreamListener):

    def __init__(self, time_limit=10):
        self.start_time = time.time()
        self.limit = time_limit
        print("time_limit = ", time_limit)
        # self.saveFile = open('abcd.json', 'a')
        super(mystreamListener, self).__init__()

    def on_data(self, data):
        if (time.time() - self.start_time) < self.limit:
            # self.saveFile.write(data)
            # self.saveFile.write('\n')
            all_tweets.append(json.loads(data))
            return True
        else:
            # self.saveFile.close()
            return False
        return True

    def on_timeout(self):
        print("we got a time out")

    def on_error(self, status):
        print(status)
