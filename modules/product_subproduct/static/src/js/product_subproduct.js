openerp.product_subproduct = function(instance, local) {
    module = instance.point_of_sale;
    var _t = instance.web._t;
    var round_pr = instance.web.round_precision;

    module.PosWidget = module.PosWidget.extend({
        build_widgets: function() {
            this._super();
            this.select_subproduct = new module.SelectSubproductPopupWidget(this, {});
            this.screen_selector.popup_set['select-subproduct'] = this.select_subproduct;
        },
    });

    module.Order = module.Order.extend({

        updateProduct: function(product, orderline_id){
           var orderline = this.getOrderline(orderline_id);
           orderline.product = product;
           orderline.trigger('change', orderline);
        }
    })

    module.Orderline = module.Orderline.extend({
        get_unit_price: function(){
            var rounding = this.pos.currency.rounding;
            var price = this.price + this.get_subproducts_price();
            return round_pr(price, rounding);

        },

        get_subproducts_price: function(){
            var subproduct_price = 0;
            if (!_.isUndefined(this.product.subproducts)) {

                for(var i=0, len=this.product.subproducts.length; i<len; i++) {
                    subproduct_price += this.product.subproducts[i].subproduct_price;
                }
            }
            return subproduct_price;
        },

        can_be_merged_with: function(orderline){
            if (!_.isUndefined(orderline.get_product().subproducts))
                return false;
            return module.Orderline.__super__.can_be_merged_with.apply(this, arguments);
        },

        export_as_JSON: function() {

            // super() for Backbone Model
            var res = module.Orderline.__super__.export_as_JSON.apply(this, arguments);

            var product = this.get_product();
            if (!_.isUndefined(product.subproducts)) {
                var config = {};
                config.bom = [];
                for(var i=0, len=product.subproducts.length; i<len; i++) {
                    config.bom.push({product_id: product.subproducts[i].subproduct_id[0]});
                }
                res.config = config;
            }

            return res;
        },

    })

    module.SelectSubproductPopupWidget = module.PopUpWidget.extend({
        template:'SelectSubproductPopupWidget',

        start: function(){
            this._super();
        },

        show: function(options){

            var options = options || {};
            var self = this;
            var previous;
            this._super();

            self.product = options.product;
            self.subproducts = options.subproducts;

            this.appendTo(this.pos_widget.$el);
            this.renderElement();

            var selected = options.selected_subproducts;
            if(selected.length > 0) {
                for(var i=0, len=selected.length; i<len; i++) {
                    var subproduct = selected[i];
                    var line = this.$('ul.select-subproduct:last').clone();
                    line.find('select').val(subproduct.id).prop('selected', true);
                    line.insertBefore('ul.select-subproduct:last');
                }

                for(var i=0, len=selected.length; i<len; i++) {
                    var subproduct = selected[i];
                    this.$('select.select-subproduct')
                    .children()
                    .filter('[value="' + subproduct.id + '"]')
                    .not(':selected')
                    .attr("hidden", "hidden");
                }
            }

            this.$('select.select-subproduct').focus(function() {
                previous = $(this).val();
            }).click(function() {
                previous = $(this).val();
            }).change(function(e){
                var last_line = self.$('ul.select-subproduct:last');
                var last_select = self.$('select.select-subproduct:last');
                if(this.value != 'choice') {
                    if(last_select[0] === e.target) {
                        last_line.clone(true).insertAfter(last_line);
                    };
                        .children()
                        .filter('[value="' + this.value + '"]')
                    );
                    self.$('select.select-subproduct').not($(this))
                        .children()
                        .filter('[value="' + this.value + '"]')
                        .attr("hidden", "hidden");
                };
                if(previous != 'choice'){
                    self.$('select.select-subproduct')
                        .children()
                        .filter('[value="'+ previous +'"]')
                        .removeProp('hidden');
                };
            });

            this.$('.delete-subproduct').click(function(e){
                n = self.$('select.select-subproduct').length;
                last_subproduct = self.$('.delete-subproduct:last');
                if(last_subproduct[0] === e.target && n == 1) {
                    self.$('select.select-subproduct:last').val('choice').prop('selected', true);
                };
                if (n > 1) {
                    var select = $(this).closest('ul').find('.select-subproduct');
                    self.$('select.select-subproduct')
                        .children()
                        .filter('[value="' + select.val() + '"]')
                        .removeProp('hidden');
                    $(this).closest('ul').remove();
                };
            });

            this.$('.button.cancel').click(function(){
                self.pos_widget.screen_selector.close_popup();
            });
            this.$('.button.ok').click(function(){
                var subproducts = [];
                self.$('select.select-subproduct').each(function(){
                    if(this.value != 'choice' && this.value != 'delete') {
                        subproducts.push(
                            self.pos.db.get_subproduct_by_id(self.product.product_tmpl_id, this.value)
                        );
                    }
                });
                self.product.subproducts = subproducts;
                self.pos_widget.screen_selector.close_popup();
                var product = jQuery.extend(true, {}, self.product);
                order = self.pos.get('selectedOrder');
                if (options.configure_line_id) {
                    order.updateProduct(product, options.configure_line_id);
                }
                else {
                    order.addProduct(product);
                }
          });
        },

    });

    module.OrderWidget = module.OrderWidget.extend({

        render_orderline: function(orderline){
            self = this;
            var template = 'Orderline';
            if (!_.isUndefined(orderline.get_product().subproducts) &&
                orderline.get_product().subproducts.length > 0) {
                template += 'WithSubproducts';
            }
            var el_str  = openerp.qweb.render(template, {widget:this, line:orderline});
            var el_node = document.createElement('div');
            el_node.innerHTML = _.str.trim(el_str);
            el_node = el_node.childNodes[0];
            el_node.orderline = orderline;
            el_node.addEventListener('click',this.line_click_handler);
            $(el_node).find('button').on('click', function() {
                var product = orderline.product;
                var subproducts = self.pos.db.get_subproducts(product.product_tmpl_id);
                params = {
                    product: product,
                    subproducts: subproducts,
                    orderline: orderline,
                    configure_line_id: orderline.id,
                    selected_subproducts: orderline.product.subproducts
                }
                self.pos.pos_widget.screen_selector.show_popup(
                    'select-subproduct', params);
            });
            orderline.node = el_node;
            return el_node;
        },

    });

    module.ProductListWidget = module.ProductListWidget.extend({

        init: function(parent, options) {
            this._super(parent, options);
            var self = this;
            self.click_product_handler_original = this.click_product_handler;

            this.click_product_handler = function(event){

                var product = self.pos.db.get_product_by_id(this.dataset['productId']);
                var subproducts = self.pos.db.get_subproducts(this.dataset['productTmpl']);
                if (subproducts.length > 0) {
                    var params = {
                        product: product,
                        subproducts: subproducts,
                        options: options,
                        configure_line_id: false,
                        selected_subproducts: []
                    };
                    self.pos.pos_widget.screen_selector.show_popup(
                        'select-subproduct', params);
                } else {
                    self.click_product_handler_original.call(this, event);
                }
            };
        },

    });

    module.PosDB = module.PosDB.extend({
        init: function(options){
            this.subproduct_by_product_id = {};
            this._super(options);
        },

        get_subproducts: function(product_id) {
            var res = [];
            var table = this.subproduct_by_product_id;
            if (product_id in table) {
                res = table[product_id];
            }
            return res
        },

        get_subproduct_by_id: function(product_id, subproduct_id) {
            var subproduct = false;
            var subproducts = this.get_subproducts(product_id);
            for (var i=0, len=subproducts.length; i<len; i++) {
                subproduct = subproducts[i];
                if (subproduct.id == subproduct_id)
                    break;
            }
            return subproduct;
        },

        add_subproducts: function(entries) {
            var table = this.subproduct_by_product_id;
            for (var i=0, len=entries.length; i < len; i++) {
                subproducts = [];
                entry = entries[i];
                product_id = entry.product_id[0];
                if (product_id in table) {
                    subproducts = table[product_id];
                }
                subproducts.push(entry);
                table[product_id] = subproducts;
            }
        },

    });

    var _initialize_ = module.PosModel.prototype.initialize;
    module.PosModel.prototype.initialize = function(session, attributes) {

        self = this;
        var subproduct_model = {
            model:  'product.subproduct',
            fields: ['subproduct_id', 'subproduct_price', 'product_id'],
            domain: null,
            loaded: function(self, subproducts) {
                self.db.add_subproducts(subproducts);
            },
        };

        for (var i = 0 ; i < this.models.length; i++){
            if (this.models[i].model == 'product.product') {
                this.models[i].fields.push('subproduct_ids');
                this.models.splice(i, 0, subproduct_model);
                i += 1;
            }
        }
        return _initialize_.call(this, session, attributes);
   };
}
