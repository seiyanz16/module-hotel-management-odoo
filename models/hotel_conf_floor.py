from odoo import fields, models, api

class HotelFloor(models.Model):
    _name = "hotel.floor"
    _description = "Hotel Floor"

    name = fields.Char(string="Floor Name", required=True)
    manager = fields.Many2many("res.partner", string="Manager")

    _sql_constraints = [
        ("name_uniq", "unique(name)", "The floor name must be unique"),
    ]