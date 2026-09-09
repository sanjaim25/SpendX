from app import ma
from app.models import User
from marshmallow import fields, validate, post_load
import bcrypt


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True
        exclude = ('password_hash',)

    name = fields.Str(
        required=True,
        validate=validate.Length(min=2, max=100)
    )
    email = fields.Email(required=True)
    password = fields.Str(
        required=True,
        validate=validate.Length(min=6),
        load_only=True
    )

    @post_load
    def hash_password(self, data, **kwargs):
        if 'password' in data:
            raw = data.pop('password')
            data.password_hash = bcrypt.hashpw(
                raw.encode(), bcrypt.gensalt()
            ).decode()
        return data


class UserLoginSchema(ma.Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)
