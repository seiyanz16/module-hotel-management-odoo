from odoo import fields, models, api
class RoomAmenities(models.Model):
    _name = "hotel.room.amenity"
    _description = "Room Amenities"

    room_id = fields.Many2one("hotel.room", string="Room", required=True, ondelete="cascade")
    amenity_id = fields.Many2one("hotel.amenity", string="Amenity", required=True)
    quantity = fields.Integer(string="Quantity", default=1, required=True)
    price = fields.Float(string="Price", required=True)
    subtotal = fields.Float(string="Subtotal", compute="_compute_subtotal", store=True)

    @api.depends('quantity', 'price')
    def _compute_subtotal(self):
        for record in self:
            record.subtotal = record.quantity * record.price

    @api.onchange('amenity_id')
    def _onchange_amenity_id(self):
        if self.amenity_id:
            self.price = self.amenity_id.product_id.list_price