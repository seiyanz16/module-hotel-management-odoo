from odoo import fields, models, api

class HotelAmenities(models.Model):
    _name = "hotel.amenity"
    _description = "Hotel Amenities"

    name = fields.Char(string="Amenities Name", required=True)
    icon = fields.Binary(string="Icon")
    product_id = fields.Many2one(
        'product.product', string="Related Product", readonly=True)

    _sql_constraints = [
        ("name_uniq", "unique(name)", "The amenities name must be unique"),
    ]

    @api.model
    def create(self, vals):
        # Create a product for the amenities
        product_vals = {
            'name': vals['name'],
            'detailed_type': 'product',
            'sale_ok': True,
            'purchase_ok': False,
            'image_1920': vals.get('icon')  # Set the icon
        }
        product = self.env['product.product'].create(product_vals)
        vals['product_id'] = product.id
        return super(HotelAmenities, self).create(vals)

    def write(self, vals):
        res = super(HotelAmenities, self).write(vals)
        for record in self:
            if 'name' in vals and record.product_id:
                # Update the product name if amenities name is updated
                record.product_id.name = vals['name']
            if 'icon' in vals and record.product_id:
                # Update the product icon if amenities icon is updated
                record.product_id.image_1920 = vals['icon']
        return res
