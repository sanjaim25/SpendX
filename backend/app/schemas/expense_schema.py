from app import ma
from app.models import Expense
from marshmallow import fields, validate, pre_load


class ExpenseSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Expense
        load_instance = True
        include_fk = True

    description = fields.Str(
        required=True,
        validate=validate.Length(min=2, max=255)
    )
    amount = fields.Float(
        required=True,
        validate=validate.Range(min=0.01)
    )
    date = fields.Date(required=False)
    predicted_category = fields.Str(dump_only=True)

    @pre_load
    def clean_data(self, data, **kwargs):
        if 'description' in data:
            data['description'] = data['description'].strip()
        return data
