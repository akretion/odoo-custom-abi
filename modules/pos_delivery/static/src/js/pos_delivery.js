/******************************************************************************
 * Point Of Sale - Product Template module for Odoo
 * Copyright (C) 2014-Today Akretion (http://www.akretion.com)
 * @author Sylvain Calador (sylvain.calador@akretion.com)
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as
 * published by the Free Software Foundation, either version 3 of the
 * License, or (at your option) any later version.
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU Affero General Public License for more details.
 * You should have received a copy of the GNU Affero General Public License
 * along with this program. If not, see <http://www.gnu.org/licenses/>.
 *****************************************************************************/

openerp.pos_delivery = function(instance, local) {
    module = instance.point_of_sale;
    var QWeb = instance.web.qweb;
    var _t = instance.web._t;
    var round_pr = instance.web.round_precision;

    module.ProductCategoriesWidget.include({

        init: function (parent, options) {
            this._super(parent, options);
        },

        renderElement: function () {
            var self = this;
            this._super();
            $('#do_delivery').click(function () {
                 self.pos_widget.screen_selector.set_current_screen('pickinglist');
            });
        },
    });

    module.PosWidget = module.PosWidget.extend({
        build_widgets: function() {
            this._super();

            this.pickinglist_screen = new module.PickingListScreenWidget(this, {});
            this.pickinglist_screen.appendTo(this.$('.screens'));
            this.pickinglist_screen.hide();

            this.pickingadjust_screen = new module.PickingAdjustScreenWidget(this, {});
            this.pickingadjust_screen.appendTo(this.$('.screens'));
            this.pickingadjust_screen.hide();

            this.screen_selector.screen_set['pickinglist'] =
                this.pickinglist_screen;

            this.screen_selector.screen_set['pickingadjust'] =
                this.pickingadjust_screen;
        },
    });

    module.PickingListScreenWidget = module.ScreenWidget.extend({
        template: 'PickingListScreenWidget',
        show_leftpane: false,

        init: function(parent, options){
            this._super(parent, options);
        },

        start: function() {
            var self = this;
            this._super();
            this.$el.find('span.button.back').click(function(){
                var ss = self.pos.pos_widget.screen_selector;
                ss.set_current_screen('products');
            });

            var search_timeout = null;

            this.$('.searchbox input').on('keyup',function(event){
                clearTimeout(search_timeout);

                var query = this.value;

                search_timeout = setTimeout(function(){
                    self.perform_search(query);
                },70);

            });

            this.$('.searchbox .search-clear').click(function(){
                self.clear_search();
            });

        },

        load_pickings: function(query) {
            var self = this;
            var stockPickingModel = new instance.web.Model('stock.picking');
            return stockPickingModel.call('search_read_pickings', [query || ''])
            .then(function (result) {
                self.render_list(result);
            }).fail(function (error, event){
                if (error.code === 200) {
                    // Business Logic Error, not a connection problem
                    self.pos_widget.screen_selector.show_popup(
                        'error-traceback', {
                            message: error.data.message,
                            comment: error.data.debug
                        }
                    );
                }
                console.error('Failed to load pickings:', query);
                self.pos_widget.screen_selector.show_popup('error',{
                    message: 'Connection error',
                    comment: 'Can not execute this action because the POS \
                        is currently offline',
                });
                event.preventDefault();
            });
        },

        show: function() {
            this._super();
            var ss = this.pos.pos_widget.screen_selector;
            if (ss.get_current_screen() == 'pickinglist') {
                this.load_pickings();
            }
        },

        render_list: function(pickings) {
            var self = this;
            var contents = this.$el[0].querySelector('.picking-list-contents');
            contents.innerHTML = "";
            for (var i = 0, len = pickings.length; i < len; i++){
                var picking = pickings[i];
                var pickingline_html = QWeb.render('PickingLine',
                    {widget: this, picking:pickings[i]});
                var pickingline = document.createElement('tbody');
                pickingline.innerHTML = pickingline_html;
                pickingline = pickingline.childNodes[1];

                var handler = (function(picking) {
                    return function() {
                        var ss = self.pos.pos_widget.screen_selector;
                        ss.set_current_screen('pickingadjust', {
                            picking: picking,
                        });
                    };
                })(picking);

                pickingline.addEventListener('click', handler);
                contents.appendChild(pickingline);
            }
        },

        perform_search: function(query) {
            this.load_pickings(query)
        },

        clear_search: function() {
            this.load_pickings();
            this.$('.searchbox input')[0].value = '';
            this.$('.searchbox input').focus();
        },

    });

    module.PickingAdjustScreenWidget = module.ScreenWidget.extend({
        template: 'PickingAdjustScreenWidget',
        show_leftpane: false,

        init: function(parent, options) {
            this._super(parent, options);
        },

        start: function() {
            var self = this;
            this._super();
            this.$el.find('span.button.back').click(function(){
                var ss = self.pos.pos_widget.screen_selector;
                ss.set_current_screen('products');
            });
            this.$el.find('span.button.validate').click(function(){
                var stockPickingModel = new instance.web.Model('stock.picking');
                var ss = self.pos.pos_widget.screen_selector;
                var picking = ss.get_current_screen_param('picking')
                ss.set_current_screen('products');
                var operations = {}
                self.$el.find('input[id^=operation_qty_]').each(function() {
                    var input_el = $(this);
                    var operation_id = input_el.attr('id').split('operation_qty_')[1];
                    var operation = {};
                    operations[operation_id] = parseFloat(input_el.val());
                });
                return stockPickingModel.call('do_detailed_transfer', [picking.id, operations]);
            });
        },

        show: function() {
            this._super();
            var ss = this.pos.pos_widget.screen_selector;
            if (ss.get_current_screen() == 'pickingadjust') {
                var picking = ss.get_current_screen_param('picking')
                if (picking !== undefined) {
                    this.load_operations(picking);
                }
            }
        },

        load_operations: function(picking) {
            var self = this;
            var stockPackOperationModel = new instance.web.Model('stock.pack.operation');
            return stockPackOperationModel.call('search_read_operations', [picking.id])
            .then(function (result) {
                self.render_list(picking, result);
            }).fail(function (error, event){
                if (error.code === 200) {
                    // Business Logic Error, not a connection problem
                    self.pos_widget.screen_selector.show_popup(
                        'error-traceback', {
                            message: error.data.message,
                            comment: error.data.debug
                        }
                    );
                }
                console.error('Failed to load operations:', picking.id);
                self.pos_widget.screen_selector.show_popup('error',{
                    message: 'Connection error',
                    comment: 'Can not execute this action because the POS \
                        is currently offline',
                });
                event.preventDefault();
            });
        },

        render_list: function(picking, operations){
            var self = this;
            var header_content = this.$el[0].querySelector('.pickingadjust-header');
            header_content.innerHTML = picking.name + ' ' + picking.partner_id[1];

            var contents = this.$el[0].querySelector('.pickingadjust-list-contents');
            contents.innerHTML = "";
            for (var i = 0, len = operations.length; i < len; i++){
                var operation = operations[i];
                var operationline_html = QWeb.render('PickingAdjustLine',
                    {widget: this, operation:operation});
                var operationline = document.createElement('tbody');
                operationline.innerHTML = operationline_html;
                operationline = operationline.childNodes[1];

                var update_qty_handler = (function(operation_line, operation) {
                    return function() {
                        var operation_id = parseInt(this.dataset['operationId']);
                        var dq = parseInt(this.dataset['dq']);
                        var field_qty = operation_line.querySelector('#operation_qty_'+operation_id);
                        var qty_value = field_qty.value;
                        var qty = isNaN(parseInt(qty_value)) ? 0 : parseInt(qty_value);
                        if (dq > 0) {
                            if ((qty + dq) <= operation.product_qty) {
                                qty += dq;
                            }
                        } else {
                            if ((qty + dq) >= 0) {
                                qty += dq;
                            }
                        }
                        qty_value = qty.toString();
                        field_qty.value = qty_value;
                    }
                })(operationline, operation);

                operationline.querySelector('button.down').addEventListener('click', update_qty_handler);
                operationline.querySelector('button.up').addEventListener('click', update_qty_handler);
                operationline.querySelector('input').addEventListener('change', function() {
                    this.value = isNaN(parseInt(this.value)) ? 0 : parseInt(this.value);
                });
                contents.appendChild(operationline);
            }
        },
    });
}
