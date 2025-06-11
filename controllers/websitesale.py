from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
import logging

_logger = logging.getLogger(__name__)


class WebsiteSaleCustom(WebsiteSale):
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
        # Forzar allowed_company_ids con todas las compañías del usuario
        env = request.env(
            context=dict(
                request.env.context,
                allowed_company_ids=request.env.user.company_ids.ids,
            )
        )

        # Log del contexto para depuración
        _logger.info("Contexto en shop: %s", env.context)
        _logger.info("website_id en contexto: %s", env.context.get("website_id"))
        _logger.info(
            "allowed_company_ids en contexto: %s",
            env.context.get("allowed_company_ids"),
        )
        _logger.info("Compañías permitidas (company_ids): %s", env.user.company_ids.ids)

        # Obtener el usuario portal conectado
        user = env.user
        company_id = (
            user.partner_id.company_id.id if user.partner_id.company_id else False
        )

        # Si el usuario tiene una compañía asignada, filtrar productos por company_id
        if company_id:
            post["company_id"] = company_id

        # Llamar al método original del shop con los parámetros modificados
        response = super(WebsiteSaleCustom, self).shop(
            page=page,
            category=category,
            search=search,
            min_price=min_price,
            max_price=max_price,
            ppg=ppg,
            **post
        )

        # Si hay un company_id, aplicar el filtro adicional
        if company_id:
            response.qcontext["products"] = response.qcontext["products"].filtered(
                lambda p: p.company_id.id == company_id
            )

        return response
