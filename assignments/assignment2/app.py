from apispec import APISpec
from apispec_fromfile import FromFilePlugin
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin
from apispec_fromfile import from_file
from flask import Flask, json, jsonify, request, session
from flasgger import Swagger
from model.model import DeeplinkSchema, BitlinkResponse, LinkClicksResponse, LinkClicksSchema
import string
import random
from datetime import datetime

spec = APISpec(
    title="SJSU Student Registration API",
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
    return jsonify({"foo": "bar"})

@app.route("/spec")
def get_apispec():
    return jsonify(spec.to_dict())

@app.route("/shorten", methods=['POST'])
def post_shorten():
    json_data = request.json
    longUrl = json_data["long_url"]
    domain = json_data["domain"]
    group_guid = json_data["group_guid"]

    ts = datetime.now()

    new_link = domain + "/" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))

    while new_link in session.keys():  
        new_link = domain + "/" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    
    deeplink = dict(guid=group_guid , 
    bitlink=new_link, created=ts, 
    modified=ts, 
    app_id="", 
    app_uri_path="", 
    install_url="", 
    install_type="")

    deeplinkObj = DeeplinkSchema().dump(deeplink)

    deeplinkArr = []

    deeplinkArr.append(deeplinkObj)

    bitlinkResponseObj = dict(deeplinks = deeplinkArr, 
    long_url = longUrl, 
    title = "", 
    tags = [])

    session[new_link] = bitlinkResponseObj

    return BitlinkResponse().dump(bitlinkResponseObj)

@app.route("/create", methods=['POST'])
def post_create():
    json_data = request.json
    longUrl = json_data["long_url"]
    domain = json_data["domain"]
    group_guid = json_data["group_guid"]
    title = json_data["title"]
    tags = json_data["tags"]
    deeplinks = json_data["deeplinks"]

    ts = datetime.now()

    new_link = domain + "/" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))

    while new_link in session.keys():  
        new_link = domain + "/" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    
    deeplink = dict(guid=group_guid , 
    bitlink=new_link, 
    created=ts, 
    modified=ts, 
    app_id=deeplinks[0]["app_id"], 
    app_uri_path=deeplinks[0]["app_uri_path"], 
    install_url=deeplinks[0]["install_url"], 
    install_type=deeplinks[0]["install_type"])

    deeplinkObj = DeeplinkSchema().dump(deeplink)

    deeplinkArr = []

    deeplinkArr.append(deeplinkObj)

    bitlinkResponseObj = dict(deeplinks = deeplinkArr, long_url = longUrl, title = title, tags = tags)

    session[new_link] = bitlinkResponseObj

    return BitlinkResponse().dump(bitlinkResponseObj)

@app.route("/bitlinks/<path:bitlink>", methods=['PATCH'])
def patch_update(bitlink):
    json_data = request.json
    longUrl = json_data["long_url"]
    group_guid = json_data["group_guid"]
    title = json_data["title"]
    archived = json_data["archived"]
    tags = json_data["tags"]
    deeplinks = json_data["deeplinks"]
    created_at = json_data["created_at"]
    created_by = json_data["created_by"]
    client_id = json_data["client_id"]
    custom_bitlinks = json_data["custom_bitlinks"]
    launchpad_ids = json_data["launchpad_ids"]

    ts = datetime.now()
    
    deeplink = dict(guid=group_guid , 
    bitlink=bitlink,
    created=ts, 
    modified=ts, 
    app_id=deeplinks[0]["app_id"], 
    app_uri_path=deeplinks[0]["app_uri_path"], 
    install_url=deeplinks[0]["install_url"], 
    install_type=deeplinks[0]["install_type"])

    deeplinkObj = DeeplinkSchema().dump(deeplink)

    deeplinkArr = []

    deeplinkArr.append(deeplinkObj)

    bitlinkResponseObj = dict(deeplinks = deeplinkArr, 
    id = client_id,
    long_url = longUrl, 
    title = title, 
    archived = archived,
    created_at = created_at,
    created_by = created_by,
    client_id = client_id,
    custom_bitlinks = custom_bitlinks,
    tags = tags,
    launchpad_ids = launchpad_ids)

    session[bitlink] = bitlinkResponseObj

    return BitlinkResponse().dump(bitlinkResponseObj)

@app.route("/retrieve", methods=['GET'])
def get_retrieve():
    json_data = request.json
    bitlink = json_data["bitlink"]

    if 'count_'+bitlink not in session:
        session['count_'+bitlink] = []

    timestampArr = session['count_'+bitlink]

    timestampArr.append(datetime.now().isoformat())

    session['count_'+bitlink] = timestampArr

    return BitlinkResponse().dump(session[bitlink])

@app.route("/bitlinks/<path:bitlink>/clicks", methods=['GET'])
def get_clicks(bitlink):
    json_data = request.json
    units = int(json_data["units"])
    unit = json_data["unit"]
    unit_reference = json_data["unit_reference"]

    if 'count_'+bitlink not in session:
        session['count_'+bitlink] = []

    count = 0
    if units:
        count = len(session['count_'+bitlink])
    else:
        if unit == "month":
            count = get_clicks_month(session['count_'+bitlink], units)
        elif unit == "week":
            count = get_clicks_week(session['count_'+bitlink], units)
        elif unit == "day":
            count = get_clicks_day(session['count_'+bitlink], units)
        elif unit == "hour":
            count = get_clicks_hour(session['count_'+bitlink], units)
        elif unit == "minute":
            count = get_clicks_minute(session['count_'+bitlink], units)
        else:
            count = get_clicks_day(session['count_'+bitlink], units)

    linkClicksDict = dict(clicks=count)

    linkClicksObj = LinkClicksSchema().dump(linkClicksDict)

    linkClicksArr = []

    linkClicksArr.append(linkClicksObj)

    linkClicksResponse = dict(link_clicks = linkClicksArr)

    return LinkClicksResponse().dump(linkClicksResponse)

def get_clicks_month(timestampArr, month):
    count = 0
    for timestamp in timestampArr:
        datetime_object_date = datetime.strptime(timestamp.split("T")[0], '%Y-%m-%d')
        if datetime_object_date.month == month:
            count += 1
    return count

def get_clicks_week(timestampArr, week):
    count = 0
    for timestamp in timestampArr:
        datetime_object_date = datetime.strptime(timestamp.split("T")[0], '%Y-%m-%d')
        if datetime_object_date.isocalendar()[1] == week:
            count += 1
    return count

def get_clicks_day(timestampArr, day):
    count = 0
    for timestamp in timestampArr:
        datetime_object_date = datetime.strptime(timestamp.split("T")[0], '%Y-%m-%d')
        if datetime_object_date.day == day:
            count += 1
    return count

def get_clicks_hour(timestampArr, hour):
    count = 0
    for timestamp in timestampArr:
        datetime_object_time = datetime.strptime(timestamp.split("T")[1], '%H:%M:%S.%f')
        if datetime_object_time.hour == hour:
            count += 1
    return count

def get_clicks_minute(timestampArr, minute):
    count = 0
    for timestamp in timestampArr:
        datetime_object_time = datetime.strptime(timestamp.split("T")[1], '%H:%M:%S.%f')
        if datetime_object_time.minute == minute:
            count += 1
    return count

with app.test_request_context():
    spec.path(view=index)
    spec.path(view=post_shorten)
    spec.path(view=post_create)
    spec.path(view=patch_update)
    spec.path(view=get_retrieve)
    spec.path(view=get_clicks)

app.run(debug=True)