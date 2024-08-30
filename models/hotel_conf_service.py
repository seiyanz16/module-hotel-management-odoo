from odoo import fields, models, api

class HotelSerivices(models.Model):
    _name = "hotel.service"
    _description = "Hotel Service"

    name = fields.Char(string="Service Name", required=True)
    price = fields.Float(string="Price", required=True)

    _sql_constraints = [
        ("name_uniq", "unique(name)", "The service name must be unique"),
    ]
