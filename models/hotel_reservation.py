from odoo import fields, models, api
from odoo.exceptions import UserError

class HotelReservation(models.Model):
    _name = "hotel.reservation"
    _description = "Hotel Reservation"

    reservation_code = fields.Char(string="Reservation Code", required=True, copy=False, readonly=True, index=True, default=lambda self: 'New')
    customer = fields.Many2one("res.partner", string="Customer", required=True)
    invoice_address = fields.Many2one("res.partner", string="Invoice Address", required=True, readonly=True)
    reserve_date = fields.Date(string="Order Date", default=fields.Date.context_today)
    state = fields.Selection(
        [("draft", "Draft"),
         ("confirm", "Confirm"),
         ("checkin", "Check-in"),
         ("checkout", "Check-out"),
         ("done", "Done"),
         ("cancel", "Cancel")], default="draft", string="Status")
    grand_total = fields.Float(string="Total", compute="_compute_grand_total", store=True)
    room_ids = fields.One2many("hotel.reservation.folio", 'reservation_id',string="Rooms")

    @api.onchange('customer')
    def _onchange_customer(self):
        if self.customer:
            self.invoice_address = self.customer

    @api.model
    def create(self, vals):
        # If the reservation_code is still 'New', generate the sequence code
        if vals.get('reservation_code', 'New') == 'New':
            vals['reservation_code'] = self.env['ir.sequence'].next_by_code(
                'hotel.reservation') or 'New'
        if not vals.get('invoice_address') and vals.get('customer'):
            vals['invoice_address'] = vals['customer']
        return super(HotelReservation, self).create(vals)

    def write(self, vals):
        if vals.get('customer'):
            vals['invoice_address'] = vals['customer']
        return super(HotelReservation, self).write(vals)

    def action_checkin(self):
        for reservation in self:
            reservation.state = 'checkin'
            # Update the status of the related rooms to "occupied"
            for folio in reservation.room_ids:
                if folio.room_id.status == 'reserved':
                    folio.room_id.status = 'occupied'
                else:
                    raise UserError(f"Room {folio.room_id.name} is not reserved and cannot be checked in.")

    def action_checkout(self):
        for reservation in self:
            reservation.state = 'checkout'
            # Update the status of the related rooms to "available"
            for folio in reservation.room_ids:
                if folio.room_id.status == 'occupied':
                    folio.room_id.status = 'available'
                else:
                    raise UserError(f"Room {folio.room_id.name} is not occupied and cannot be checked out.")

    def action_done(self):
        for reservation in self:
            reservation.state = 'done'

    def action_cancel(self):
        for reservation in self:
            reservation.state = 'cancel'
            for folio in reservation.room_ids:
                folio.room_id.status = 'available'

    def action_reserve(self):
        for reservation in self:
            if reservation.state == 'draft':
                reservation.state = 'confirm'
                # Update the status of the related rooms to "reserved"
                for folio in reservation.room_ids:
                    if folio.room_id.status == 'available':
                        folio.room_id.status = 'reserved'
                    else:
                        raise UserError(
                            f"Room {folio.room_id.name} is not available for reservation.")
            else:
                raise UserError(
                    "Reservation must be in Draft state to be reserved.")

    @api.depends('room_ids.subtotal')
    def _compute_grand_total(self):
            for record in self:
                record.grand_total = sum(record.room_ids.mapped('subtotal'))

    def unlink(self):
        for record in self:
            if record.state not in ['done', 'cancel']:
                raise UserError(
                    ("You cannot delete a reservation that is not completed or canceled."))
        return super(HotelReservation, self).unlink()
