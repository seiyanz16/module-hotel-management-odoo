{
    "name": "Hotel Management",
    "version": "17.0.1.0.0",
    "category": "Addons",
    "summary": "Hotel Management is an addons for Odoo 17 to manage Hotel", 
    "description": """Hotel Management is an addons for Odoo 17 to manage Hotel""",
    "author": "Zaskia",
    "company": "KDJ's Company",
    "maintainer": "ERP Team KDJ's Company",
    "depends": ["product", "uom"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/hotel_wizard_reservation.xml",
        "report/hotel_reservation_report.xml",
        "report/hotel_reservation_template.xml",
        "views/hotel_menu.xml",
        "views/hotel_conf_amenity.xml",
        "views/hotel_conf_floor.xml",
        "views/hotel_conf_room.xml",
        "views/hotel_conf_service.xml",
        "views/hotel_reservation.xml",
    ],
    "assets": {},
    "installable": True,
    "auto-install": False,
    "application": True,
}
