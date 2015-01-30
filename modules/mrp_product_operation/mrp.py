# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015-TODAY Akretion (<http://www.akretion.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import logging

from openerp import models, fields, api, _

_logger = logging.getLogger(__name__)


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.model
    def _prepare_workcenter_data(self, product):
        return {
            'workcenter_id': product.routing_workcenter_id.workcenter_id.id,
            'name': product.routing_workcenter_id.name,
            'hour': product.hour_nbr,
        }

    @api.model
    def _get_mrp_data_from_config(
            self, production, product, product_data, workcenter_data):
        config = production.move_prod_id.procurement_id.sale_line_id.config
        if not config:
            return (product_data, workcenter_data)
        config_workcenter_data = []
        if 'operation_ids' in config:
            for product_operation in self.env['product.product'].browse(
                    config['operation_ids']):
                if (product_operation.type in ('product', 'consu')
                        and product_operation.is_operation):
                    workc_data = self._prepare_workcenter_data(
                        product_operation)
                    if workc_data:
                        config_workcenter_data.append(workc_data)

                    condition = [('product_tmpl_id',
                                  '=',
                                  product_operation.product_tmpl_id.id
                                  )]
                    bom_operation = self.env['mrp.bom'].search(condition)
                    if bom_operation:
                        factor = self.env['product.uom']._compute_qty(
                            production.product_uom.id,
                            production.product_qty,
                            bom_operation.product_uom.id
                        )
                        component_data, workcenter_data = \
                            self.env['mrp.bom'].with_context(
                                production=False)._bom_explode(
                                bom_operation, product, factor)

                        product_data.extend(component_data)

        if not config_workcenter_data:
            config_workcenter_data = list(workcenter_data)
        return (product_data, config_workcenter_data)
