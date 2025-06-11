from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
import logging

_logger = logging.getLogger(__name__)


class WebsiteSaleCustom(WebsiteSale):
    def sale_product_domain(self):
        domain = super().sale_product_domain()
        domain = [
            d for d in domain if not (isinstance(d, tuple) and d[0] == "company_id")
        ]
        _logger.info("Dominio en sale_product_domain: %s", domain)
        return domain

    def _shop_lookup_products(self, attrib_set, options, post, search, website):
        # Loguear el dominio y contexto antes de la búsqueda
        domain = self._get_shop_domain(
            search, options.get("category"), options.get("attrib_values")
        )
        _logger.info("Dominio en _shop_lookup_products: %s", domain)
        _logger.info("Contexto en _shop_lookup_products: %s", request.env.context)

        return super()._shop_lookup_products(attrib_set, options, post, search, website)

    @http.route()
    def shop(
        self,
        page=0,
        category=None,
        search="",
        min_price=0.0,
        max_price=0.0,
        ppg=False,
        **post
    ):
        env = request.env(
            context=dict(
                request.env.context,
                allowed_company_ids=request.env.user.company_ids.ids,
                website_id=request.website.id,
            )
        )

        _logger.info("Contexto en shop: %s", env.context)
        _logger.info("website_id en contexto: %s", env.context.get("website_id"))
        _logger.info(
            "allowed_company_ids en contexto: %s",
            env.context.get("allowed_company_ids"),
        )
        _logger.info("Compañías permitidas (company_ids): %s", env.user.company_ids.ids)
        _logger.info(
            "Compañía del sitio web (website.company_id): %s",
            request.website.company_id.id,
        )

        user = env.user
        company_id = (
            user.partner_id.company_id.id if user.partner_id.company_id else False
        )

        if company_id:
            post["company_id"] = company_id

        response = super(WebsiteSaleCustom, self).shop(
            page=page,
            category=category,
            search=search,
            min_price=min_price,
            max_price=max_price,
            ppg=ppg,
            **post
        )

        if company_id:
            response.qcontext["products"] = response.qcontext["products"].filtered(
                lambda p: p.company_id.id == company_id
            )

        return response
