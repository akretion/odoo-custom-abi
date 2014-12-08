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
    'name': 'Subproduct',
    'version': '0.1',
    'author': 'Akretion',
    'category': 'Sales Management',
    'depends': ['base', 'decimal_precision', 'product', 'point_of_sale', 'web', 'pos_product_template'],
    'demo': [],
    'website': 'https://www.akretion.com',
    'description': """
This module allow to define subproducts of a product
and display these subproduct on the POS vendor interface
    """,
    'data': [
        'security/subproduct_security.xml',
        'security/ir.model.access.csv',
        'product_view.xml',
        'views/product_subproduct.xml',
    ],
    'qweb': [
        'static/src/xml/subproduct.xml',
    ],  
    'test': [],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
