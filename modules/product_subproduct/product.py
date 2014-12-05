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
import openerp.addons.decimal_precision as dp

_logger = logging.getLogger(__name__)


class product_subproduct(models.Model):
    _name = 'product.subproduct'
    _rec_name = 'subproduct_id'
    
    subproduct_id = fields.Many2one('product.product', string=u'Subproduct', required=True)
    subproduct_price = fields.Float('Price', digits_compute=dp.get_precision('Product Price'))
    product_id = fields.Many2one('product.template', string=u'Main product', required=True)

class product_template(models.Model):
    _inherit = 'product.template'
    
    subproduct_ids = fields.One2many('product.subproduct', 'product_id', string='Subproducts')

