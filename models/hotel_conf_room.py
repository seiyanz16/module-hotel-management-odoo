from odoo import fields, models, api

class HotelRoom(models.Model):
    _name = "hotel.room"
    _description = "Hotel Room"

    name = fields.Char(string="Room Name", required=True)
    status = fields.Selection(
        [("available", "Available"), 
         ("reserved", "Reserved"), 
         ("occupied", "Occupied")], default="available", string="Status", required=True)
    rent = fields.Float(string="Rent", required=True)
    attachment = fields.Binary(string="Attachment", max_width=1024, max_height=1024)

    floor_id = fields.Many2one("hotel.floor", string="Floor", required=True)
    manager = fields.Many2one("res.partner", string="Room Manager", readonly=True)
    room_type = fields.Char(string="Room Type", required=True)
    number_of_persons = fields.Integer(string="Number of Persons", required=True)
    cost = fields.Float(string="Cost", readonly=True, compute="_compute_cost")
    amenity_ids = fields.One2many("hotel.room.amenity", "room_id", string="Amenities")
    description = fields.Html(string="Description")
    grand_total = fields.Float(
        string="Total", compute="_compute_grand_total", store=True)

    _sql_constraints = [
        ("name_uniq", "unique(name)", "The room name must be unique"),
    ]


    @api.depends('rent', 'amenity_ids.subtotal')
    def _compute_cost(self):
        for room in self:
            total_amenities_cost = sum(
                amenity.subtotal for amenity in room.amenity_ids)
            room.cost = total_amenities_cost
    @api.onchange('floor_id')
    def _onchange_floor_id(self):
        if self.floor_id:
            self.manager = self.floor_id.manager.id
        else:
            self.manager = False

    @api.model
    def create(self, vals):
        if 'floor_id' in vals:
            floor = self.env['hotel.floor'].browse(vals['floor_id'])
            vals['manager'] = floor.manager.id
        return super(HotelRoom, self).create(vals)

    def write(self, vals):
        if 'floor_id' in vals:
            floor = self.env['hotel.floor'].browse(vals['floor_id'])
            vals['manager'] = floor.manager.id
        return super(HotelRoom, self).write(vals)
    
    @api.depends('amenity_ids.subtotal')
    def _compute_grand_total(self):
        for record in self:
            record.grand_total = sum(record.amenity_ids.mapped('subtotal'))
