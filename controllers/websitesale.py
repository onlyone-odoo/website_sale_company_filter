# -*- coding: utf-8 -*-
# ¡No olvides importar los módulos de logging y expression!
import logging
from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.osv import expression

# Obtenemos una instancia del logger. Los mensajes aparecerán en tu log de Odoo.
_logger = logging.getLogger(__name__)


class WebsiteSaleCustom(WebsiteSale):
    def _get_shop_domain(
        self, search, category, attrib_values, search_in_description=True
    ):
        """
        Versión de depuración con LOGS para trazar el flujo de filtrado de productos por compañía.
        """
        _logger.info(
            "---[DEBUG COMPAÑÍA]---> Iniciando _get_shop_domain personalizado."
        )

        user = request.env.user
        _logger.info(
            f"---[DEBUG COMPAÑÍA]---> Usuario actual: {user.name} (ID: {user.id})"
        )

        # Vamos a verificar las condiciones paso a paso
        is_portal = user.has_group("base.group_portal")
        _logger.info(
            f"---[DEBUG COMPAÑÍA]---> ¿Es usuario del grupo portal?: {is_portal}"
        )

        partner = user.partner_id
        _logger.info(
            f"---[DEBUG COMPAÑÍA]---> Partner asociado: {partner.name} (ID: {partner.id})"
        )

        partner_company = partner.company_id
        _logger.info(
            f"---[DEBUG COMPAÑÍA]---> Compañía del partner: '{partner_company.name if partner_company else 'NINGUNA'}' (ID: {partner_company.id if partner_company else 'N/A'})"
        )

        # La condición completa que decide qué lógica aplicar
        is_portal_user_with_company = is_portal and bool(partner_company)
        _logger.info(
            f"---[DEBUG COMPAÑÍA]---> Resultado de la condición (is_portal_user_with_company): {is_portal_user_with_company}"
        )

        if not is_portal_user_with_company:
            _logger.info(
                "---[DEBUG COMPAÑÍA]---> DECISIÓN: Usando lógica estándar de Odoo (super)."
            )
            super_domain = super(WebsiteSaleCustom, self)._get_shop_domain(
                search, category, attrib_values, search_in_description
            )
            _logger.info(
                f"---[DEBUG COMPAÑÍA]---> Dominio estándar devuelto por super(): {super_domain}"
            )
            return super_domain

        # --- Lógica personalizada para usuarios de portal con compañía ---
        _logger.info(
            f"---[DEBUG COMPAÑÍA]---> DECISIÓN: Aplicando lógica personalizada para la compañía ID: {partner_company.id}"
        )

        domains = [
            [("sale_ok", "=", True)],
            [("is_published", "=", True)],
            [("company_id", "=", partner_company.id)],
        ]
        _logger.info(f"---[DEBUG COMPAÑÍA]---> Dominio base construido: {domains}")

        if search:
            _logger.info(
                f"---[DEBUG COMPAÑÍA]---> Añadiendo filtro de búsqueda por texto: '{search}'"
            )
            # ... (la lógica de búsqueda se mantiene) ...
        if category:
            _logger.info(
                f"---[DEBUG COMPAÑÍA]---> Añadiendo filtro de categoría ID: {category}"
            )
            # ... (la lógica de categoría se mantiene) ...
        if attrib_values:
            _logger.info(
                f"---[DEBUG COMPAÑÍA]---> Añadiendo filtro de atributos: {attrib_values}"
            )
            # ... (la lógica de atributos se mantiene) ...

        # Replicamos la lógica original completa para no perder funcionalidad
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

        final_domain = expression.AND(domains)
        _logger.info(
            f"---[DEBUG COMPAÑÍA]---> DOMINIO FINAL CONSTRUIDO: {final_domain}"
        )

        return final_domain
