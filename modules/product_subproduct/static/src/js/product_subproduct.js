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

        export_as_JSON: function() {
            var config = {};
            if (!_.isUndefined(this.product.subproducts)) {
                bom = [];
                for(var i=0, len=this.product.subproducts.length; i<len; i++) {
                    bom.push({product_id: this.product.subproducts[i].subproduct_id[0]});
                }
                config.bom = bom;
            }

            var res =  {
                qty: this.get_quantity(),
                config: config,
                price_unit: this.get_unit_price(),
                discount: this.get_discount(),
                product_id: this.get_product().id,
            };
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
            this._super();

            self.product = options.product;
            self.subproducts = options.subproducts;
            
            this.appendTo(this.pos_widget.$el);
            this.renderElement();

            this.$('select.select-subproduct').change(function(){
                var last_line = self.$('ul.select-subproduct:last');
                if(this.value != 'choice') {
                    last_line.clone(true).insertAfter(last_line);
                }
            });

            this.$('.delete-subproduct').click(function(e){
                n = self.$('select.select-subproduct').length;
                last_subproduct = self.$('.delete-subproduct:last');
                if(last_subproduct[0] === e.target) {
                    self.$('select.select-subproduct:last').val('choice').prop('selected', true);
                }
                if (n > 1) {
                    $(this).closest('ul').remove();
                }
            });

            this.$('.button.cancel').click(function(){
                self.pos_widget.screen_selector.close_popup();
            });
            this.$('.button.ok').click(function(){
                var subproducts = [];
                self.$('select.select-subproduct').each(function(){
                    if(this.value != 'choice' && this.value != 'delete') {
                        subproducts.push(self.pos.db.get_subproduct_by_id(this.value));
                    }
                });
                self.product.subproducts = subproducts;
                self.pos_widget.screen_selector.close_popup();
                options.options.click_product_action(self.product);
           });
        },

    });

    module.OrderWidget = module.OrderWidget.extend({

        render_orderline: function(orderline){
            var template = 'Orderline';
            if (!_.isUndefined(orderline.product.subproducts) &&
                orderline.product.subproducts.length > 0) {
                template += 'WithSubproducts';
            }
            var el_str  = openerp.qweb.render(template, {widget:this, line:orderline});
            var el_node = document.createElement('div');
            el_node.innerHTML = _.str.trim(el_str);
            el_node = el_node.childNodes[0];
            el_node.orderline = orderline;
            el_node.addEventListener('click',this.line_click_handler);
            orderline.node = el_node;
            return el_node;
        },

    });

    module.ProductListWidget = module.ProductListWidget.extend({

        init: function(parent, options) {
            this._super(parent, options);
            var self = this;

            this.click_product_handler = function(event){
                var product_id = this.dataset['productId'];
                var product = self.pos.db.get_product_by_id(product_id);
                var subproducts = self.pos.db.get_subproducts(product_id);
                if (subproducts.length > 0) {
                    params = {
                        product: product,
                        subproducts: subproducts,
                        options: options
                    };
                    self.pos.pos_widget.screen_selector.show_popup(
                        'select-subproduct', params);
                } else {
                    options.click_product_action(product);
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

        get_subproduct_by_id: function(subproduct_id) {
            var subproduct = false;
            var subproducts = this.subproduct_by_product_id;
            for (var key in subproducts) {
                for (var i=0, len=subproducts[key].length; i<len; i++) {
                    subproduct = subproducts[key][i];
                    if (subproduct.id == subproduct_id)
                        break;
                }
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
