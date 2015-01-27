# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 Akretion (<http://www.akretion.com>).
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
from openerp.exceptions import Warning
import openerp.addons.decimal_precision as dp

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    operation_ids = fields.Many2many(
        'product.product',
        domain=[('is_operation', '=', True)],
        string='Operations')
    is_operation = fields.Boolean('Is Operation')
    routing_workcenter_id = fields.Many2one(
        'mrp.routing.workcenter',
        string='Operation',
        readonly=True,
        help="")
    hour_nbr = fields.Float(
        related='routing_workcenter_id.hour_nbr',
        string="Nbr d'heures",
        readonly=True)
    workcenter_id = fields.Char(
        related="routing_workcenter_id.workcenter_id.name",
        string="Poste de charge",
        readonly=True)

    @api.model
    def create_routing_workc(self, name):
        MrpRtWc = self.env['mrp.routing.workcenter']
        MrpWc = self.env['mrp.workcenter']
        # TODO need to have a default workcenter in settings (by company or antenne)
        workc_ids = MrpWc.search([])
        if not workc_ids:
            Warning(_("You need to create at least one workcenter \n"
                      "to define product operations"))
        routing_id = self.env.ref(
            'mrp_product_operation.mrp_product_operation_generic').id
        vals = {
            'routing_id': routing_id,
            'name': name,
            'workcenter_id': workc_ids[0].id}
        return MrpRtWc.create(vals)

    @api.model
    def create(self, vals):
        if 'is_operation' in vals:
            if vals['is_operation']:
                vals['routing_workcenter_id'] = self.create_routing_workc(
                    vals['name']).id
        vals['sale_ok'] = False
        return super(ProductTemplate, self).create(vals)

    @api.one
    def write(self, vals):
        # TODO   if vals['is_operation'] == False:
        # TODO      search product_id ds ls m2m des otres prds et raise si o - 1 prd
        # TODO   else:
        # TODO      check pas de produit le m2m prds operation ds le prd en cours
        MrpRtWc = self.pool['mrp.routing.workcenter']
        if 'is_operation' in vals:
            if vals['is_operation']:
                vals['sale_ok'] = False
                name = self.name
                if 'name' in vals:
                    name = vals['name']
                vals['routing_workcenter_id'] = self.create_routing_workc(
                    name).id
            else:
                MrpRtWc.unlink(self.routing_workcenter_id)
                vals['routing_workcenter_id'] = False
        return super(ProductTemplate, self).write(vals)

    @api.multi
    def unlink(self, ids):
        ""
        # TODO: Delete operation when delete product
