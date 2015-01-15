# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 Akretion (<http://www.akretion.com>).
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

from openerp import models, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.model
    def search_read_pickings(self, query):
        if (query):
            condition = ['|',
                         ('partner_id', 'ilike', query),
                         ('name', 'ilike', query),
                         ]
        else:
            condition = []
        fields = ['id', 'name', 'partner_id']
        return self.search_read(condition, fields, limit=10)


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.model
    def search_read_moves(self, query):
        condition = [('picking_id', '=', query)]
        fields = ['id', 'product_id', 'product_qty']
        res = self.search_read(condition, fields)
        product_ids = [r['product_id'][0] for r in res]
        product_obj = self.env['product.product']
        products = product_obj.browse(product_ids)
        display_names = {}
        for product in products:
            display_names[product.id] = product.display_name
        result = []
        for r in res:
            result.append({
                'id': r['id'],
                'product': display_names[r['product_id'][0]],
                'product_qty': r['product_qty'],
            })
        return result
