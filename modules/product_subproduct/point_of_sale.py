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


from openerp import models, api


class PosOrder(models.Model):
    _inherit = 'pos.order'

    @api.model
    def pos_order_filter(self, orders_dict):
        res = []
        for order_dict in orders_dict:
            order = self.env['sale.order'].browse(order_dict['id'])
            pos_order = True
            for order_line in order.order_line:
                if not order_line.product_id.available_in_pos:
                    pos_order = False
                    break
            if pos_order:
                res.append(order_dict)

        return res

    @api.model
    def search_read_orders(self, query):
        condition = [
            ('state', '=', 'draft'),
            '|',
            ('name', 'ilike', query),
            ('partner_id', 'ilike', query)
        ]
        fields = ['name', 'partner_id']
        sale_obj = self.env['sale.order']
        res = sale_obj.search_read(condition, fields, limit=10)
        return self.pos_order_filter(res)

    @api.one
    def load_order(self):
        condition = [('order_id', '=', self.id)]
        fields = ['product_id', 'price_unit', 'product_uom_qty', 'discount']
        lines = self.env['sale.order.line'].search_read(condition, fields)
        orderlines = []
        for line in lines:
            line['qty'] = line.pop('product_uom_qty')
            product_id = line['product_id'][0]
            product = self.env['product.product'].browse(product_id)
            if not product.available_in_pos:
                raise Warning('''
                    This order can\'t be loaded because it contains
                    product not available on the POS
                ''')
            if product.product_tmpl_id.subproduct_ids:
                # TODO inject pos/sale order lines saved subproducts (read from
                # config field)
                line.update({'product__subproducts': []})
            orderlines.append(line)

        order_dict = {
            'partner_id': self.partner_id and self.partner_id.id or False,
            'orderlines': orderlines
        }

        return order_dict
