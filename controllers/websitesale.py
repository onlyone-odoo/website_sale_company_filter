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

        # Comprobar si el visitante es un usuario de portal y tiene una compañía asignada.
        is_portal_user_with_company = (
            user.has_group("base.group_portal") and user.partner_id.company_id
        )

        # SI NO es nuestro usuario especial, dejamos que Odoo siga su curso normal.
        # Esto ejecutará la lógica original que tú encontraste, filtrando por 'website_id'.
        if not is_portal_user_with_company:
            return super(WebsiteSaleCustom, self)._get_shop_domain(
                search, category, attrib_values, search_in_description
            )

        # --- LÓGICA PERSONALIZADA SOLO PARA USUARIOS DE PORTAL CON COMPAÑÍA ---
        # A partir de aquí, ignoramos la lógica por defecto y construimos nuestro propio dominio.

        # 1. Creamos un dominio base que filtra por la compañía del usuario.
        #    Ya NO llamamos a la lógica que filtra por 'website_id'.
        #    Agregamos 'sale_ok' y 'is_published' que son esenciales para la tienda.
        domains = [
            [("sale_ok", "=", True)],
            [("is_published", "=", True)],
            [("company_id", "=", user.partner_id.company_id.id)],
        ]

        # 2. Replicamos el resto de la lógica de filtros del método original
        #    para que la búsqueda por texto, categorías y atributos siga funcionando.
        if search:
            for srch in search.split(" "):
                subdomains = [
                    [("name", "ilike", srch)],
                    [("product_variant_ids.default_code", "ilike", srch)],
                ]
                if search_in_description:
                    subdomains.append([("website_description", "ilike", srch)])
                    subdomains.append([("description_sale", "ilike", srch)])

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

        # 3. Combinamos todos nuestros dominios en uno solo.
        return expression.AND(domains)
