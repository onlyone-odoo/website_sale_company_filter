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
        Hereda el método para sobreescribir completamente el dominio de búsqueda de productos
        cuando un usuario de portal con una compañía específica está conectado.
        """
        user = request.env.user

        # Comprobar si es un usuario de portal y si tiene una compañía asignada en su contacto.
        # El grupo 'base.group_portal' identifica a los usuarios del portal.
        is_portal_user_with_company = (
            user.has_group("base.group_portal") and user.partner_id.company_id
        )

        if not is_portal_user_with_company:
            # Para usuarios públicos, internos o sin compañía, usar la lógica por defecto de Odoo.
            return super(WebsiteSaleCustom, self)._get_shop_domain(
                search, category, attrib_values, search_in_description
            )

        # --- Lógica personalizada para usuarios de portal con compañía ---
        # A partir de aquí, construimos un nuevo dominio desde cero para este tipo de usuario.

        # 1. El dominio base ahora se filtra por la compañía del usuario.
        #    También agregamos el chequeo 'sale_ok' que es fundamental para el e-commerce.
        domains = [
            [("sale_ok", "=", True)],
            [("company_id", "=", user.partner_id.company_id.id)],
        ]

        # 2. Replicamos la lógica del método original para los otros filtros (búsqueda, categoría, etc.)
        #    para no perder la funcionalidad del shop.
        if search:
            for srch in search.split(" "):
                subdomains = [
                    [("name", "ilike", srch)],
                    [("product_variant_ids.default_code", "ilike", srch)],
                ]
                if search_in_description:
                    subdomains.append([("website_description", "ilike", srch)])
                    subdomains.append([("description_sale", "ilike", srch)])

                # Hook para extensiones de otros módulos (buena práctica mantenerlo)
                extra_subdomain = self._add_search_subdomains_hook(srch)
                if extra_subdomain:
                    subdomains.append(extra_subdomain)

                domains.append(expression.OR(subdomains))

        if category:
            domains.append([("public_categ_ids", "child_of", int(category))])

        if attrib_values:
            attrib = None
            ids = []
            for value in attrib_values:
                if not attrib:
                    attrib = value[0]
                    ids.append(value[1])
                elif value[0] == attrib:
                    ids.append(value[1])
                else:
                    domains.append([("attribute_line_ids.value_ids", "in", ids)])
                    attrib = value[0]
                    ids = [value[1]]
            if attrib:
                domains.append([("attribute_line_ids.value_ids", "in", ids)])

        # 3. Combinamos todos los dominios con un AND.
        return expression.AND(domains)
