from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSaleCustom(WebsiteSale):
    @http.route()
    def shop(self, page=0, category=None, search="", **post):
        # Obtener compañías del usuario conectado
        user_companies = request.env.user.company_id
        # Modificar dominio para incluir solo productos de las compañías del usuario
        domain = [("website_published", "=", True)]
        if user_companies:
            domain += [
                "|",
                ("company_id", "in", user_companies.id),
                ("company_id", "=", False),
            ]
        # Llamar al método original con el dominio modificado
        return super(WebsiteSaleCustom, self).shop(
            page=page, category=category, search=search, domain=domain, **post
        )
