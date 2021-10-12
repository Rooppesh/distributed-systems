from marshmallow import Schema, fields


class StudentSchema(Schema):
    id = fields.Int()
    first_name = fields.Str(required=True)
    last_name = fields.Str(required=True)
    sjsu_id = fields.Str(required=True)
    email = fields.Email()
    create_timestamp = fields.DateTime(format="timestamp")
    update_timestamp = fields.DateTime(format="timestamp")
