# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.osv import expression


class WebsiteSaleCustom(WebsiteSale):
    def _get_shop_domain(
        self, search, category, attrib_values, search_in_description=True
    ):
        """
        Hereda el método original para agregar un filtro de productos por compañía
        basado en el usuario del portal que ha iniciado sesión.
        """
        # Llama al método original para obtener el dominio base
        domain = super(WebsiteSaleCustom, self)._get_shop_domain(
            search, category, attrib_values, search_in_description
        )

        # Obtiene el usuario del portal y su compañía asignada
        user = request.env.user

        # Se asegura de que el usuario sea un usuario del portal (no un usuario interno o público)
        is_portal_user = user.has_group("base.group_portal")

        if is_portal_user and user.partner_id.company_id:
            # Crea el dominio adicional para filtrar por la compañía del usuario
            company_domain = [("company_id", "=", user.partner_id.company_id.id)]

            # Combina el dominio original con el nuevo dominio usando expression.AND
            # Esto asegura que todos los filtros (búsqueda, categoría, etc.) se mantengan
            domain = expression.AND([domain, company_domain])

        return domain
