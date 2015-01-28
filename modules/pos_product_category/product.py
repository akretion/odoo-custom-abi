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

from openerp import tools, SUPERUSER_ID
from openerp import models, fields, api, _
from openerp.exceptions import Warning


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    pos_categ_id = fields.Many2one('product.category',
                                   store=True, related='categ_id')

    @api.multi
    def write(self, vals):
        if 'pos_categ_id' in vals and not vals['pos_categ_id']:
            del vals['pos_categ_id']
        return super(ProductTemplate, self).write(vals)

    def _auto_init(self, cr, context=None):
        context = context or {}

        # avoid integrity errors due to pos_categ_id model redefinition
        cr.execute('''
            SELECT 1 FROM product_template
            WHERE
                categ_id != pos_categ_id OR
                pos_categ_id IS NULL
        ''')
        if cr.fetchone():
            cr.execute('ALTER TABLE product_template DROP COLUMN pos_categ_id')

        return super(ProductTemplate, self)._auto_init(cr, context=context)
