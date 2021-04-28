{
    "name": "Apty Website Promo",
    "summary": "Allow to use same coupon single time",
    "version": "13.0.1.0.1",
    "category": "Website",
    "website": "",
    "author": "Mayank Nailwal",
    "license": "AGPL-3",
    "depends": ["base", "website_sale", "sale_coupon"],
    "data": [
        # "security/ir.model.access.csv",
        "views/res_partner_inherit_view.xml",
        "views/sale_coupon_program_view.xml",
    ],
    "installable": True,
}