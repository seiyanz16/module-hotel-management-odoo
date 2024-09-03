from odoo import fields, models, api

class HotelReservationRoom(models.Model):
    _name = "hotel.reservation.folio"
    _description = "Hotel Reservation Room"

    reservation_id = fields.Many2one("hotel.reservation", string="Reservation", required=True, ondelete="cascade")
    room_id = fields.Many2one("hotel.room", string="Room", required=True, ondelete="cascade")
    checkin = fields.Datetime(string="Check-In", required=True)
    checkout = fields.Datetime(string="Check-Out", required=True)
    duration = fields.Integer(string="Duration", compute="_compute_duration", store=True)
    uom_id = fields.Many2one("uom.uom", string="UoM", required=True)
    rent = fields.Float(string="Rent", required=True)
    subtotal = fields.Float(string="Subtotal", compute="_compute_subtotal", store=True)

    @api.onchange('room_id')
    def _onchange_room_id(self):
        if self.room_id:
            self.rent = self.room_id.rent

    @api.depends('checkin', 'checkout')
    def _compute_duration(self):
        for record in self:
            checkin_date = fields.Datetime.from_string(record.checkin)
            checkout_date = fields.Datetime.from_string(record.checkout)
            if checkin_date and checkout_date:
                record.duration = (checkout_date - checkin_date).days
            else:
                record.duration = 0

    @api.depends('duration', 'rent')
    def _compute_subtotal(self):
        for record in self:
            record.subtotal = record.duration * record.rent
            
    # autofill uom with days 
    @api.onchange('duration')
    def _onchange_duration(self):
        if self.duration:
            self.uom_id = self.env.ref('uom.product_uom_day')