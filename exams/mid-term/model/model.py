import string
from marshmallow import Schema, fields

class TweetSchema(Schema):
    user_id = fields.Int(required=True)
    tweet_id = fields.Int(required=True)
    tweet = fields.Str(required=True)

class TwitterResponseSchema(Schema):
    id = fields.Int(required=True)
    name = fields.Str(required=True)
    email = fields.Email(required=True)
    tweets = fields.List(fields.Nested(TweetSchema))
    followers = fields.List(fields.Str)

class TimelineSchema(Schema):
    timeline = fields.List(fields.Nested(TweetSchema))