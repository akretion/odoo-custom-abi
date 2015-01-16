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
import csv
import re


class product_template(orm.Model):
    _inherit = 'product.template'

    _columns = {
        'tmpl_code': fields.char('Template code')
        }


class product_product(orm.Model):
    _inherit = "product.product"

    _columns = {
        'from_magento': fields.boolean('From magento'),
        }

    def _import_product(self, cr, uid, import_file, gamme_1_id, gamme_2_id, gamme_3_id, mode=False, context=None):
        if mode:
            self._import_product_spe_mode(cr, uid, import_file, gamme_1_id, gamme_2_id, gamme_3_id, context=context)
        else:
            self._import_product_normal(cr, uid, import_file, gamme_1_id, gamme_2_id, gamme_3_id, context=context)
        return True

    def _import_product_spe_mode(self, cr, uid, import_file, gamme_1_id, gamme_2_id, gamme_3_id, context=None):
        template_obj = self.pool['product.template']
        attribute_obj = self.pool['product.attribute']
        value_obj = self.pool['product.attribute.value']
        categ_obj = self.pool['product.category']
        line_obj = self.pool['product.attribute.line']
        data_obj = self.pool['ir.model.data']
        file_count = csv.DictReader(import_file, delimiter=",")
        total_row = len(list(file_count))
        import_file.seek(0)
        file_dict = csv.DictReader(import_file, delimiter=",")
        current_row = 0
        if context is None:
            context = {}
        model, categ_parent_id = data_obj.get_object_reference(
            cr, uid, 'product', 'product_category_1')
        no_categ = []
        no_name = []
        for row in file_dict:
            decoded_row = {}
            for key, value in row.items():
# TODO choose in the wizard ?
                if not isinstance(key, unicode) and key:
                    key = unicode(key, "ISO-8859-15")
                if not isinstance(value, unicode) and value:
                    value = unicode(value, "ISO-8859-15")
                decoded_row[key] = value
            current_row += 1
# product template
            tmpl_code = decoded_row['Code'][:7]
            template_ids = template_obj.search(
                cr, uid, [('tmpl_code', '=', tmpl_code)], context=context)
            if not template_ids:
                # remove () and last space
                name = re.sub("[\(].*?[\)]", "", decoded_row[u'Designation'])[:-1]
                if not name:
                    no_name.append(decoded_row['Code'])
                template_vals = {
                    'tmpl_code': tmpl_code,
                    'name': name,
                    'type': 'product',
                    }
                categ_name = decoded_row['CodeFam']
                if categ_name:
                    categ_ids = categ_obj.search(
                        cr, uid, [('name', '=', categ_name)], context=context)
                    if not categ_ids:
                        categ_id = categ_obj.create(cr, uid,
                                                    {'name': categ_name,
                                                     'parent_id': categ_parent_id},
                                                    context=context)
                    else:
                        categ_id = categ_ids[0]
                    template_vals['categ_id'] = categ_id
                else:
                    no_categ.append(decoded_row['Code'])
                ctx = context.copy()
                ctx['create_product_product'] = True
                template_id = template_obj.create(cr, uid, template_vals,
                                                  context=ctx)
                line_1_id = line_obj.create(
                    cr, uid, {'product_tmpl_id': template_id,
                              'attribute_id': gamme_1_id},
                    context=context)
                line_2_id = line_obj.create(
                    cr, uid, {'product_tmpl_id': template_id,
                              'attribute_id': gamme_2_id},
                    context=context)
                if gamme_3_id:
                    line_3_id = line_obj.create(
                        cr, uid, {'product_tmpl_id': template_id,
                                  'attribute_id': gamme_3_id},
                        context=context)
            else:
                template_id = template_ids[0]
                line_1_id = line_obj.search(
                    cr, uid, [('product_tmpl_id', '=', template_id),
                              ('attribute_id', '=', gamme_1_id)],
                    context=context)[0]
                line_2_id = line_obj.search(
                    cr, uid, [('product_tmpl_id', '=', template_id),
                              ('attribute_id', '=', gamme_2_id)],
                    context=context)[0]
                if gamme_3_id:
                    line_3_id = line_obj.search(
                        cr, uid, [('product_tmpl_id', '=', template_id),
                                  ('attribute_id', '=', gamme_3_id)],
                        context=context)[0]
# product product
            default_code = decoded_row['Code']
            product_ids = self.search(
                cr, uid, [('default_code', '=', default_code)], context=context)
            if not product_ids:
                value_ids = []
                if gamme_1_id and decoded_row['Gamme1']:
                    value_1_ids = value_obj.search(
                        cr, uid,
                        [('name', '=', decoded_row['Gamme1']),
                         ('attribute_id', '=', gamme_1_id)],
                        context=context)
                    if not value_1_ids:
                        value_1_id = value_obj.create(
                            cr, uid, {'name': decoded_row['Gamme1'],
                                      'attribute_id': gamme_1_id},
                            context=context)
                        line_obj.write(
                            cr, uid, line_1_id, {'value_ids': [(4, value_1_id)]},
                            context=context)
                        value_ids.append((4, value_1_id))
                    else:
                        line_1_ids = line_obj.search(
                            cr, uid, [('id', '=', line_1_id),
                                      ('value_ids', 'in', [value_1_ids[0]])],
                            context=context)
                        if not line_1_ids:
                            line_obj.write(
                                cr, uid, line_1_id,
                                {'value_ids': [(4, value_1_ids[0])]},
                                context=context)
                        value_ids.append((4, value_1_ids[0]))
                if gamme_2_id and decoded_row['Gamme2']:
                    value_2_ids = value_obj.search(
                        cr, uid,
                        [('name', '=', decoded_row['Gamme2']),
                         ('attribute_id', '=', gamme_2_id)],
                        context=context)
                    if not value_2_ids:
                        value_2_id = value_obj.create(
                            cr, uid, {'name': decoded_row['Gamme2'],
                                      'attribute_id': gamme_2_id},
                            context=context)
                        line_obj.write(
                            cr, uid, line_2_id, {'value_ids': [(4, value_2_id)]},
                            context=context)
                        value_ids.append((4, value_2_id))
                    else:
                        line_2_ids = line_obj.search(
                            cr, uid, [('id', '=', line_2_id),
                                      ('value_ids', 'in', [value_2_ids[0]])],
                            context=context)
                        if not line_2_ids:
                            line_obj.write(
                                cr, uid, line_2_id,
                                {'value_ids': [(4, value_2_ids[0])]},
                                context=context)
                        value_ids.append((4, value_2_ids[0]))
                if gamme_3_id and decoded_row['Gamme3']:
                    value_3_ids = value_obj.search(
                        cr, uid,
                        [('name', '=', decoded_row['Gamme3']),
                        ('attribute_id', '=', gamme_3_id)],
                        context=context)
                    if not value_3_ids:
                        value_3_id = value_obj.create(
                            cr, uid, {'name': decoded_row['Gamme3'],
                                      'attribute_id': gamme_3_id},
                            context=context)
                        line_obj.write(
                            cr, uid, line_3_id, {'value_ids': [(4, value_3_id)]},
                            context=context)
                        value_ids.append((4, value_3_id))
                    else:
                        line_3_ids = line_obj.search(
                            cr, uid, [('id', '=', line_3_id),
                                      ('value_ids', 'in', [value_3_ids[0]])],
                            context=context)
                        if not line_3_ids:
                            line_obj.write(
                                cr, uid, line_3_id,
                                {'value_ids': [(4, value_3_ids[0])]},
                                context=context)
                        value_ids.append((4, value_3_ids[0]))
                product_vals = {
                    'product_tmpl_id': template_id,
                    'default_code': default_code,
                    'attribute_value_ids': value_ids,
                    'from_magento': True,
                    }
                product_id = self.create(cr, uid, product_vals, context=context)
            else:
#TODO 
                print 'todo'
            print "%s/%s" % (current_row, total_row)
        print no_categ
        return True

    def _import_product_normal(self, cr, uid, import_file, gamme_1_id, gamme_2_id, gamme_3_id, context=None):
        template_obj = self.pool['product.template']
        attribute_obj = self.pool['product.attribute']
        value_obj = self.pool['product.attribute.value']
        categ_obj = self.pool['product.category']
        line_obj = self.pool['product.attribute.line']
        data_obj = self.pool['ir.model.data']
        file_count = csv.DictReader(import_file, delimiter=";")
        total_row = len(list(file_count))
        import_file.seek(0)
        file_dict = csv.DictReader(import_file, delimiter=";")
        current_row = 0
        if context is None:
            context = {}
        model, categ_parent_id = data_obj.get_object_reference(
            cr, uid, 'product', 'product_category_1')
        no_categ = []
        no_name = []
        for row in file_dict:
            decoded_row = {}
            for key, value in row.items():
# TODO choose in the wizard ?
                if not isinstance(key, unicode) and key:
                    key = unicode(key, "ISO-8859-15")
                if not isinstance(value, unicode) and value:
                    value = unicode(value, "ISO-8859-15")
                decoded_row[key] = value
            current_row += 1
# product template
            tmpl_code = decoded_row['Code'][:7]
            template_ids = template_obj.search(
                cr, uid, [('tmpl_code', '=', tmpl_code)], context=context)
            if not template_ids:
                # remove () and last space
                name = re.sub("[\(].*?[\)]", "", decoded_row[u'Désignation'])[:-1]
                if not name:
                    no_name.append(decoded_row['Code'])
                template_vals = {
                    'tmpl_code': tmpl_code,
                    'name': name,
                    'type': 'product',
                    }
                categ_name = decoded_row['Code Famille']
                if categ_name:
                    categ_ids = categ_obj.search(
                        cr, uid, [('name', '=', categ_name)], context=context)
                    if not categ_ids:
                        categ_id = categ_obj.create(cr, uid,
                                                    {'name': categ_name,
                                                     'parent_id': categ_parent_id},
                                                    context=context)
                    else:
                        categ_id = categ_ids[0]
                    template_vals['categ_id'] = categ_id
                else:
                    no_categ.append(decoded_row['Code'])
                ctx = context.copy()
                ctx['create_product_product'] = True
                template_id = template_obj.create(cr, uid, template_vals,
                                                  context=ctx)
                line_1_id = line_obj.create(
                    cr, uid, {'product_tmpl_id': template_id,
                              'attribute_id': gamme_1_id},
                    context=context)
                line_2_id = line_obj.create(
                    cr, uid, {'product_tmpl_id': template_id,
                              'attribute_id': gamme_2_id},
                    context=context)
                if gamme_3_id:
                    line_3_id = line_obj.create(
                        cr, uid, {'product_tmpl_id': template_id,
                                  'attribute_id': gamme_3_id},
                        context=context)
            else:
                template_id = template_ids[0]
                line_1_id = line_obj.search(
                    cr, uid, [('product_tmpl_id', '=', template_id),
                              ('attribute_id', '=', gamme_1_id)],
                    context=context)[0]
                line_2_id = line_obj.search(
                    cr, uid, [('product_tmpl_id', '=', template_id),
                              ('attribute_id', '=', gamme_2_id)],
                    context=context)[0]
                if gamme_3_id:
                    line_3_id = line_obj.search(
                        cr, uid, [('product_tmpl_id', '=', template_id),
                                  ('attribute_id', '=', gamme_3_id)],
                        context=context)[0]
# product product
            default_code = decoded_row['Code']
            product_ids = self.search(
                cr, uid, [('default_code', '=', default_code)], context=context)
            if not product_ids:
                value_ids = []
                if gamme_1_id and decoded_row['Gamme 1']:
                    value_1_ids = value_obj.search(
                        cr, uid,
                        [('name', '=', decoded_row['Gamme 1']),
                         ('attribute_id', '=', gamme_1_id)],
                        context=context)
                    if not value_1_ids:
                        value_1_id = value_obj.create(
                            cr, uid, {'name': decoded_row['Gamme 1'],
                                      'attribute_id': gamme_1_id},
                            context=context)
                        line_obj.write(
                            cr, uid, line_1_id, {'value_ids': [(4, value_1_id)]},
                            context=context)
                        value_ids.append((4, value_1_id))
                    else:
                        line_1_ids = line_obj.search(
                            cr, uid, [('id', '=', line_1_id),
                                      ('value_ids', 'in', [value_1_ids[0]])],
                            context=context)
                        if not line_1_ids:
                            line_obj.write(
                                cr, uid, line_1_id,
                                {'value_ids': [(4, value_1_ids[0])]},
                                context=context)
                        value_ids.append((4, value_1_ids[0]))
                if gamme_2_id and decoded_row['Gamme 2']:
                    value_2_ids = value_obj.search(
                        cr, uid,
                        [('name', '=', decoded_row['Gamme 2']),
                         ('attribute_id', '=', gamme_2_id)],
                        context=context)
                    if not value_2_ids:
                        value_2_id = value_obj.create(
                            cr, uid, {'name': decoded_row['Gamme 2'],
                                      'attribute_id': gamme_2_id},
                            context=context)
                        line_obj.write(
                            cr, uid, line_2_id, {'value_ids': [(4, value_2_id)]},
                            context=context)
                        value_ids.append((4, value_2_id))
                    else:
                        line_2_ids = line_obj.search(
                            cr, uid, [('id', '=', line_2_id),
                                      ('value_ids', 'in', [value_2_ids[0]])],
                            context=context)
                        if not line_2_ids:
                            line_obj.write(
                                cr, uid, line_2_id,
                                {'value_ids': [(4, value_2_ids[0])]},
                                context=context)
                        value_ids.append((4, value_2_ids[0]))
                if gamme_3_id and decoded_row['Gamme 3']:
                    value_3_ids = value_obj.search(
                        cr, uid,
                        [('name', '=', decoded_row['Gamme 3']),
                        ('attribute_id', '=', gamme_3_id)],
                        context=context)
                    if not value_3_ids:
                        value_3_id = value_obj.create(
                            cr, uid, {'name': decoded_row['Gamme 3'],
                                      'attribute_id': gamme_3_id},
                            context=context)
                        line_obj.write(
                            cr, uid, line_3_id, {'value_ids': [(4, value_3_id)]},
                            context=context)
                        value_ids.append((4, value_3_id))
                    else:
                        line_3_ids = line_obj.search(
                            cr, uid, [('id', '=', line_3_id),
                                      ('value_ids', 'in', [value_3_ids[0]])],
                            context=context)
                        if not line_3_ids:
                            line_obj.write(
                                cr, uid, line_3_id,
                                {'value_ids': [(4, value_3_ids[0])]},
                                context=context)
                        value_ids.append((4, value_3_ids[0]))
                product_vals = {
                    'product_tmpl_id': template_id,
                    'default_code': default_code,
                    'attribute_value_ids': value_ids,
                    }
                product_id = self.create(cr, uid, product_vals, context=context)
            else:
#TODO 
                print 'todo'
            print "%s/%s" % (current_row, total_row)
        print 'no categ', no_categ
        print 'no name', no_name
        return True
