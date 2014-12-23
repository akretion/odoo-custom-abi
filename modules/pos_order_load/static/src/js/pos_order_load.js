openerp.pos_order_load = function(instance, local) {
    module = instance.point_of_sale;
    var QWeb = instance.web.qweb;
    var _t = instance.web._t;
    var round_pr = instance.web.round_precision;

    module.LoadButtonWidget = module.PosBaseWidget.extend({
        template: 'LoadButtonWidget',
        init: function(parent, options){
            options = options || {};
            this._super(parent, options);
        },
        start: function() {
            var self = this;
            this.$el.click(function(){
                var ss = self.pos.pos_widget.screen_selector;
                ss.set_current_screen('orderlist');
            });
        },
        show: function(){
            this.$el.removeClass('oe_hidden');
        },
        hide: function(){
            this.$el.addClass('oe_hidden');
        }
    });

    module.PosWidget = module.PosWidget.extend({
        build_widgets: function() {
            this._super();

            this.orderlist_screen = new module.OrderListScreenWidget(this, {});
            this.orderlist_screen.appendTo(this.$('.screens'));
            this.orderlist_screen.hide();

            this.load_button = new module.LoadButtonWidget(this);
            this.load_button.appendTo(this.$('li.orderline.empty'));

            this.screen_selector.screen_set['orderlist'] = this.orderlist_screen;
        },
    });

    module.OrderWidget = module.OrderWidget.extend({
        renderElement: function(scrollbottom){
            this._super(scrollbottom);
            if (this.pos_widget.load_button) {
                this.pos_widget.load_button.appendTo(
                    this.pos_widget.$('li.orderline.empty')
                );
            }
        }
    });

    module.OrderListScreenWidget = module.ScreenWidget.extend({
        template: 'OrderListScreenWidget',
        show_leftpane: true,

        init: function(parent, options){
            this._super(parent, options);
        },

        start: function() {
            var self = this;
            this._super()
            this.$el.find('span.button.back').click(function(){
                order = self.pos.get('selectedOrder');
                order.set_client(undefined);
                order.get('orderLines').reset();
                self.pos_widget.order_widget.change_selected_order();
                var ss = self.pos.pos_widget.screen_selector;

                ss.set_current_screen('products');
            });
            this.$el.find('span.button.validate').click(function(){
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

        // to override if necessary
        add_product_attribute: function(product, key, orderline){
            return product;
        },

        load_order: function(order_id) {
            var self = this;
            var posOrderModel = new instance.web.Model('pos.order');
            return posOrderModel.call('load_order', [order_id])
            .then(function (result) {
                var order = self.pos.get('selectedOrder');
                order.get('orderLines').reset();

                var partner = self.pos.db.get_partner_by_id(result.partner_id);
                if (partner){
                    order.set_client(partner);
                }

                orderlines = result.orderlines;
                for (var i=0, len=orderlines.length; i<len; i++) {
                    var orderline = orderlines[i];
                    var product_id = orderline.product_id[0];
                    var product = self.pos.db.get_product_by_id(product_id);
                    var options = {
                        quantity: orderline.qty,
                        price: orderline.price_unit,
                        discount: orderline.discount,
                    }

                    for (key in orderline) {
                        if(!key.indexOf('product__')) {
                            product = self.add_product_attribute(
                                    product, key, orderline
                            );
                        }
                    }
                    order.addProduct(product, options);
                    last_orderline = order.getLastOrderline();
                    last_orderline = jQuery.extend(last_orderline, orderline);
                }

            }).fail(function (error, event){
                if(error.code === 200 ){    // Business Logic Error, not a connection problem
                    self.pos_widget.screen_selector.show_popup('error-traceback',{
                        message: error.data.message,
                        comment: error.data.debug
                    });
                }
                console.error('Failed to load order:', order_id);
                self.pos_widget.screen_selector.show_popup('error',{
                    message: 'Connection error',
                    comment: 'Can not execute this action because the POS is currently offline',
                });
                event.preventDefault();
            });
        },

        load_orders: function(query) {
            var self = this;
            var posOrderModel = new instance.web.Model('pos.order');
            return posOrderModel.call('search_read_orders', [query || ''])
            .then(function (result) {
                self.render_list(result);
            }).fail(function (error, event){
                if(error.code === 200 ){    // Business Logic Error, not a connection problem
                    self.pos_widget.screen_selector.show_popup('error-traceback',{
                        message: error.data.message,
                        comment: error.data.debug
                    });
                }
                console.error('Failed to load orders:', query);
                self.pos_widget.screen_selector.show_popup('error',{
                    message: 'Connection error',
                    comment: 'Can not execute this action because the POS is currently offline',
                });
                event.preventDefault();
            });
        },

        show: function() {
            this._super();
            var ss = this.pos.pos_widget.screen_selector;
            if (ss.get_current_screen() == 'orderlist') {
                this.load_orders();
            }
        },

        render_list: function(orders){
            var self = this;
            var contents = this.$el[0].querySelector('.order-list-contents');
            contents.innerHTML = "";
            for(var i = 0, len = orders.length; i < len; i++){
                var order = orders[i];
                var orderline_html = QWeb.render('LoadOrderLine',{widget: this, order:orders[i]});
                var orderline = document.createElement('tbody');
                orderline.innerHTML = orderline_html;
                orderline = orderline.childNodes[1];
                orderline.addEventListener('click', function() {
                    self.load_order(parseInt(this.dataset['orderId']));
                });
                contents.appendChild(orderline);
            }
        },


        perform_search: function(query){
            if(query){
                this.load_orders(query)
            }else{
                this.load_orders();
            }
        },
        clear_search: function(){
            this.load_orders();
            this.$('.searchbox input')[0].value = '';
            this.$('.searchbox input').focus();
        },


    });

}
