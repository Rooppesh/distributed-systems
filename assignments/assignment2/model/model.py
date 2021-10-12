import string
from marshmallow import Schema, fields

class DeeplinkSchema(Schema):
    guid = fields.Str(required=True)
    bitlink = fields.Str(required=True)
    app_uri_path = fields.Str(required=True)
    install_url = fields.Str(required=True)
    app_guid = fields.Str(required=True)
    os = fields.Str(required=True)
    install_type = fields.Str(required=True)
    created = fields.Str(required=True)
    modified = fields.Str(required=True)
    brand_guid = fields.Str(required=True)

class BitlinkResponse(Schema):
    references = fields.Nested(fields.Str)
    link = fields.Str(required=True)
    id = fields.Str(required=True)
    long_url = fields.Str(required=True)
    archived = fields.Str(required=True)
    custom_bitlinks = fields.List(fields.Str)
    tags = fields.List(fields.Str)
    deeplinks = fields.List(fields.Nested(DeeplinkSchema))


class LinkClicksSchema(Schema):
    clicks = fields.Int(required=True)
    date = fields.Str(required=True)

class LinkClicksResponse(Schema):
    link_clicks = fields.List(fields.Nested(LinkClicksSchema))
    units = fields.Int(required=True)
    unit = fields.Str(required=True)
    unit_reference = fields.Str(required=True)