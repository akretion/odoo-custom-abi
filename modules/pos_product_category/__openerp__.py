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

{
    'name': 'POS Product Category',
    'version': '0.1',
    'author': 'Akretion',
    'category': 'Sales Management',
    'depends': [
        'base',
        'decimal_precision',
        'product',
        'point_of_sale',
    ],
    'demo': [],
    'website': 'https://www.akretion.com',
    'description': """
        This module allows to use main product categories in the POS
    """,
    'data': [
        'views/pos_product_category.xml',
    ],
    'qweb': [
        #'static/src/xml/pos_delivery.xml',
    ],
    'test': [],
    'installable': True,
    'auto_install': False,
}
