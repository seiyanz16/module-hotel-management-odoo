from odoo import fields, models, api
from odoo.exceptions import UserError


class HotelReservation(models.Model):
    _name = "hotel.reservation"
    _description = "Hotel Reservation"

    reservation_code = fields.Char(string="Reservation Code", required=True, copy=False, readonly=True, index=True, default="New")
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
    room_ids = fields.One2many("hotel.reservation.folio", 'reservation_id', string="Rooms")

    @api.onchange('customer')
    def _onchange_customer(self):
        if self.customer:
            self.invoice_address = self.customer

    def _generate_reservation_code(self):
        last_reservation = self.search(
            [('reservation_code', '!=', 'New')], order='id desc', limit=1)
        if last_reservation:
            last_code = last_reservation.reservation_code
            last_number = int(last_code.split('/')[-1])
            new_number = last_number + 1
        else:
            new_number = 1

        new_code = 'BOOKING/{:06d}'.format(new_number)
        return new_code

    @api.model
    def create(self, vals):
        # Ensure invoice_address is set during creation
        if 'customer' in vals and not vals.get('invoice_address'):
            vals['invoice_address'] = vals['customer']

        # Generate reservation code
        if vals.get('reservation_code', 'New') == 'New':
            vals['reservation_code'] = self._generate_reservation_code()

        return super(HotelReservation, self).create(vals)

    def write(self, vals):
        # Ensure invoice_address is updated if customer is updated
        if vals.get('customer'):
            vals['invoice_address'] = vals['customer']
        return super(HotelReservation, self).write(vals)

    def action_checkin(self):
        for reservation in self:
            reservation.state = 'checkin'
            for folio in reservation.room_ids:
                if folio.room_id.status == 'reserved':
                    folio.room_id.status = 'occupied'
                else:
                    raise UserError(
                        f"Room {folio.room_id.name} is not reserved and cannot be checked in.")

    def action_checkout(self):
        for reservation in self:
            reservation.state = 'checkout'
            for folio in reservation.room_ids:
                if folio.room_id.status == 'occupied':
                    folio.room_id.status = 'available'
                else:
                    raise UserError(
                        f"Room {folio.room_id.name} is not occupied and cannot be checked out.")

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
            if reservation.state == 'draft' and reservation.room_ids:
                reservation.state = 'confirm'
                for folio in reservation.room_ids:
                    if folio.room_id.status == 'available':
                        folio.room_id.status = 'reserved'
                    else:
                        raise UserError(
                            f"Room {folio.room_id.name} is not available for reservation.")
            else:
                raise UserError(
                    "Rooms must be selected before changing state to be reserved.")

    @api.depends('room_ids.subtotal')
    def _compute_grand_total(self):
        for record in self:
            record.grand_total = sum(record.room_ids.mapped('subtotal'))

    def unlink(self):
        for record in self:
            if record.state not in ['done', 'cancel']:
                raise UserError(
                    "You cannot delete a reservation that is not completed or canceled.")
        return super(HotelReservation, self).unlink()
