from odoo import models, fields, api
from odoo.exceptions import ValidationError

class HotelReservationReportWizard(models.TransientModel):
    _name = 'hotel.reservation.report.wizard'
    _description = 'Hotel Reservation Report Wizard'

    checkin_date = fields.Date(string="Check-In Date", required=True)
    checkout_date = fields.Date(string="Check-Out Date", required=True)
    room_id = fields.Many2one('hotel.room', string="Room")

    def action_print_report(self):
        # Define the domain to filter the reservations based on the wizard input
        domain = [
            ('checkin', '>=', self.checkin_date),
            ('checkout', '<=', self.checkout_date)
        ]

        # Filter by room if a room is selected
        if self.room_id:
            domain.append(('room_id', '=', self.room_id.id))

        # Get reservations based on the domain
        reservations = self.env['hotel.reservation.folio'].search(domain)

        # Raise an error if no reservations are found
        if not reservations:
            raise ValidationError(
                "No reservations found for the selected criteria.")

        # Generate the report
        report_action = self.env.ref(
            'hotel_management.action_report_reservation')

        if not report_action:
            raise ValidationError("Report action not found.")

        # Pass the records to the report
        return report_action.report_action(reservations)
