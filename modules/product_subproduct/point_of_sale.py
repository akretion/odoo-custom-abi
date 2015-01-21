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

    @api.one
    def load_order(self):
        order_dict = super(PosOrder, self).load_order()[0]

        # inject subproducts in order lines
        orderlines = []
        product_obj = self.env['product.product']
        for orderline in order_dict['orderlines']:
            product_id = orderline['product_id'][0]
            product = product_obj.browse(product_id)
            if product.product_tmpl_id.subproduct_ids:
                # TODO inject pos/sale order lines saved subproducts (read from
                # config field)
                orderline.update({'product__subproducts': []})
            orderlines.append(orderline)
        order_dict['orderlines'] = orderlines
        return order_dict
