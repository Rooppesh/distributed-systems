from marshmallow import Schema, fields

class DeeplinkSchema(Schema):
    long_url = fields.Str(required=True)
    bitlink = fields.Str(required=True)
    created = fields.Str(required=True)
    modified = fields.Str(required=True)