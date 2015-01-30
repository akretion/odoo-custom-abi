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

{
    'name': 'POS helper',
    'version': '0.1',
    'author': 'Akretion',
    'category': 'Sales Management',
    'depends': [
        'base',
        'web',
        'decimal_precision',
        'product',
        'point_of_sale',
        'pos_product_category',
        'pos_product_template',
        'pos_sale_order_load',
        'pos_mrp_product_operation',
        'sale_force_lot_number',
    ],
    'demo': [],
    'website': 'https://www.akretion.com',
    'description': """
        POS glue code
    """,
    'data': [
        'views/pos_helper.xml',
    ],
    'qweb': [
    ],
    'test': [],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
