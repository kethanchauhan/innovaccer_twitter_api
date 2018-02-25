from django.db import models, connection
from django.conf import settings as django_settings
from datetime import datetime, timedelta
from email.utils import parsedate
from django.utils import timezone
import os
import socket
from twitter_app import settings
import dateutil.parser
from django.core.paginator import Paginator

class Tweet(models.Model):

    # tweet info
    tweet_id = models.BigIntegerField()
    text = models.CharField(max_length=250)
    truncated = models.BooleanField(default=False)
    lang = models.CharField(max_length=9, null=True, blank=True, default=None)

    # user info
    user_id = models.BigIntegerField()
    user_screen_name = models.CharField(max_length=50)
    user_name = models.CharField(max_length=150)
    user_verified = models.BooleanField(default=False)
    user_location = models.CharField(max_length=150, null=True, blank=True, default=None)

    # Timing parameters
    created_at = models.DateTimeField(db_index=True)  # should be UTC
    user_utc_offset = models.IntegerField(null=True, blank=True, default=None)
    user_time_zone = models.CharField(max_length=150, null=True, blank=True, default=None)


    favorite_count = models.PositiveIntegerField(null=True, blank=True)
    retweet_count = models.PositiveIntegerField(null=True, blank=True)
    user_followers_count = models.PositiveIntegerField(null=True, blank=True)
    user_friends_count = models.PositiveIntegerField(null=True, blank=True)

    def __unicode__(self):
        return self.user_screen_name + " " + self.tweet_id

    @classmethod
    def create_from_json(cls, raw):
        user = raw['user']
        return cls.objects.create(
            # tweet info
            tweet_id=raw['id'],
            text=raw['text'],
            truncated=raw['truncated'],
            lang=raw.get('lang'),

            # user info
            user_id=user['id'],
            user_screen_name=user['screen_name'],
            user_name=user['name'],
            user_verified=user['verified'],

            # Timing parameters
            created_at=dateutil.parser.parse(raw['created_at']),
            user_utc_offset=user.get('utc_offset'),
            user_time_zone=user.get('time_zone'),
            user_location=user.get('location'),

            favorite_count=raw.get('favorite_count'),
            retweet_count=raw.get('retweet_count'),
            user_followers_count=raw.get('user_followers_count'),
            user_friends_count=raw.get('user_friends_count')
        )

    @classmethod
    def get_created_in_range(cls, start, end, page_no):
        tweets = cls.objects.filter(created_at__gte = start, created_at__lte=end ).order_by('-created_at')
        paginator = Paginator(tweets, 5)
        return paginator.page(page_no)

    @classmethod
    def filter_retweet_count(cls, type, r_count, page_no):
        r_count = r_count.strip()
        type = type.strip()
        if type == 'greater':
            tweets = cls.objects.filter(retweet_count__gt=int(r_count)).order_by('-retweet_count')
        if type == 'lesser':
            tweets = cls.objects.filter(retweet_count__lt=int(r_count)).order_by('-retweet_count')
        if type == 'greater_or_equal':
            tweets = cls.objects.filter(retweet_count__gte=int(r_count)).order_by('-retweet_count')
        if type == 'lesser_or_equal':
            tweets = cls.objects.filter(retweet_count__lte=int(r_count)).order_by('-retweet_count')
        if type == 'equal':
            tweets = cls.objects.filter(retweet_count=int(r_count)).order_by('-retweet_count')
        paginator = Paginator(tweets, 5)
        return paginator.page(page_no)

    @classmethod
    def filter_favorite_count(cls, type, f_count, page_no):
        f_count = f_count.strip()
        type = type.strip()
        if type == 'greater':
            tweets = cls.objects.filter(favorite_count__gt=int(f_count)).order_by('-favorite_count')
        if type == 'lesser':
            tweets = cls.objects.filter(favorite_count__lt=int(f_count)).order_by('-favorite_count')
        if type == 'greater_or_equal':
            tweets = cls.objects.filter(favorite_count__gte=int(f_count)).order_by('-favorite_count')
        if type == 'lesser_or_equal':
            tweets = cls.objects.filter(favorite_count__lte=int(f_count)).order_by('-favorite_count')
        if type == 'equal':
            tweets = cls.objects.filter(favorite_count=int(f_count)).order_by('-favorite_count')
        paginator = Paginator(tweets, 5)
        return paginator.page(page_no)

    @classmethod
    def filter_screen_name(cls, type, screen_name, page_no): # ordered by relavance
        screen_name = screen_name.strip()
        type = type.strip()
        if type == 'starts_with':
            tweets = cls.objects.filter(user_screen_name__startswith = screen_name)
        if type == 'ends_with':
            tweets = cls.objects.filter(user_screen_name__endswith = screen_name)
        if type == 'contains':
            tweets = cls.objects.filter(user_screen_name__contains= screen_name)
        if type == 'exact_match':
            tweets = cls.objects.filter(user_screen_name = screen_name)
        paginator = Paginator(tweets, 5)
        return paginator.page(page_no)

    @classmethod
    def filter_user_name(cls, type, user_name, page_no): # ordered by relavance
        user_name = user_name.strip()
        type = type.strip()
        if type == 'starts_with':
            tweets = cls.objects.filter(user_name__startswith=user_name)
        if type == 'ends_with':
            tweets = cls.objects.filter(user_name__endswith=user_name)
        if type == 'contains':
            tweets = cls.objects.filter(user_name__contains=user_name)
        if type == 'exact_match':
            tweets = cls.objects.filter(user_name=user_name)
        paginator = Paginator(tweets, 5)
        return paginator.page(page_no)

    @classmethod
    def filter_text(cls, type, text, page_no):  # ordered by relavance
        text = text.strip()
        type = type.strip()
        if type == 'starts_with':
            tweets = cls.objects.filter(text__startswith=text)
        if type == 'ends_with':
            tweets = cls.objects.filter(text__endswith=text)
        if type == 'contains':
            tweets = cls.objects.filter(text__contains=text)
        if type == 'exact_match':
            tweets = cls.objects.filter(text=text)
        paginator = Paginator(tweets, 5)
        return paginator.page(page_no)

