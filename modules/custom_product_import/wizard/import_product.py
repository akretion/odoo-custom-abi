# -*- coding: utf-8 -*-
###############################################################################
#
#   Module for OpenERP
#   Copyright (C) 2015 Akretion (http://www.akretion.com). All Rights Reserved
#   @author Benoît GUILLOT <benoit.guillot@akretion.com>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from openerp.osv import fields, orm
from tempfile import TemporaryFile
import base64

class import_product(orm.TransientModel):
    _name = "import.product"
    _description = "Import product"

    _columns = {
        'product_file': fields.binary('Import file'),
        'gamme_1_id': fields.many2one('product.attribute', 'Gamme 1'),
        'gamme_2_id': fields.many2one('product.attribute', 'Gamme 2'),
        'gamme_3_id': fields.many2one('product.attribute', 'Gamme 3'),
        'spe_mode': fields.boolean('Special mode'),
    }

    def import_product(self, cr, uid, ids, context=None):
        assert len(ids) == 1, 'Import product may only be done one at a time.'
        wizard = self.browse(cr, uid, ids[0], context=context)
        product_file = TemporaryFile('w+b')
        product_file.write(base64.decodestring(wizard.product_file))
        product_file.seek(0)
        self.pool['product.product']._import_product(
            cr, uid, product_file, wizard.gamme_1_id.id,
            wizard.gamme_2_id.id, wizard.gamme_3_id.id, mode=wizard.spe_mode,
            context=context)
        return True

