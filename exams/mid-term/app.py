from apispec import APISpec
from apispec_fromfile import FromFilePlugin
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin
from apispec_fromfile import from_file
from flask import Flask, json, jsonify, request, session
from flasgger import Swagger
from model.model import TwitterResponseSchema, TweetSchema, TimelineSchema
import string
import random
from datetime import datetime

spec = APISpec(
    title="Twitter API",
    version="0.0.1",
    openapi_version="3.0.3",
    plugins=[
        FlaskPlugin(),
        MarshmallowPlugin()
    ],
)

app = Flask(__name__)
app.secret_key = "secret key"
swagger = Swagger(app)  

@app.route("/")
def index():
    session.clear()
    return jsonify({"Session": "Cleared"})

@app.route("/spec")
def get_apispec():
    return jsonify(spec.to_dict())

@app.route("/users", methods=['POST'])
def create_user():
    json_data = request.json
    name = json_data["name"]
    email = json_data["email"]

    userIdKey = "id_count"

    id = 0

    if (userIdKey in session.keys()):
        id = session[userIdKey]
    
    id += 1

    session[userIdKey] = id

    userObj = dict(id = id, 
    name = name, 
    email = email, 
    tweets = [],
    followers = [])

    session[str(id)] = userObj

    return TwitterResponseSchema().dump(userObj)

@app.route("/users/<path:user_id>/followers/<path:follower_id>", methods=["PATCH"])
def create_follower(user_id, follower_id):

    followKey = "_follows"

    follows = []

    if (follower_id+followKey in session.keys()):
        follows = session[follower_id+followKey]

    follows.append(user_id)

    session[follower_id+followKey] = follows

    userObj = session[user_id]

    followers = []

    followers = userObj["followers"]

    followers.append(follower_id)

    userObj["followers"] = followers

    session[str(user_id)] = userObj

    return TwitterResponseSchema().dump(userObj)

@app.route("/users/<path:user_id>/tweets", methods = ["POST"])
def create_tweet(user_id):
    json_data = request.json
    tweet = json_data["tweet"]

    tweetIdKey = "tweet_id_count"

    id = 0

    if (tweetIdKey in session.keys()):
        id = session[tweetIdKey]
    
    id += 1

    session[tweetIdKey] = id

    tweetObj = dict(tweet_id = id, 
    tweet = tweet)

    tweetsKey = "_tweets"

    tweets = []

    if (user_id+tweetsKey in session.keys()):
        tweets = session[user_id+tweetsKey]

    tweets.append(json.dumps(TweetSchema().dump(tweetObj)))

    session[user_id+tweetsKey] = tweets

    return TweetSchema().dump(tweetObj)

@app.route("/users/<path:user_id>")
def get_user(user_id):

    userObj = session[str(user_id)]

    tweetsKey = "_tweets"

    tweets = []

    if (user_id+tweetsKey in session.keys()):
        tweets = session[user_id+tweetsKey]

    jsonTweets = []
    for tweet in tweets:
        jsonTweets.append(json.loads(tweet))

    userObj["tweets"] = jsonTweets

    return TwitterResponseSchema().dump(userObj)

@app.route("/users/<path:user_id>/timeline")
def get_timeline(user_id):

    followKey = "_follows"

    follows = []

    if (user_id+followKey in session.keys()):
        follows = session[user_id+followKey]

    timelineTweets = []
    for user in follows:
        tweetsKey = "_tweets"

        tweets = []

        if (user+tweetsKey in session.keys()):
            tweets = session[user+tweetsKey]

        for tweet in tweets:
            jsonTweet = json.loads(tweet)
            jsonTweet["user_id"] = user
            timelineTweets.append(jsonTweet)

    timelineObj = dict(timeline = timelineTweets)

    print(timelineObj)

    return TimelineSchema().dump(timelineObj)

with app.test_request_context():
    spec.path(view=index)
    spec.path(view=create_user)
    spec.path(view=create_follower)
    spec.path(view=create_tweet)
    spec.path(view=get_user)
    spec.path(view=get_timeline)

app.run(debug=True)
