openerp.pos_helper = function(instance, local) {
    module = instance.point_of_sale;
    var _t = instance.web._t;
    var round_pr = instance.web.round_precision;

    module.OrderListScreenWidget = module.OrderListScreenWidget.extend({

        add_product_attribute: function(product, key, orderline){
            this._super(arguments);
            var product_key = key.split('__')[1];
            if (product_key == 'operations') {

                var operations = [];
                var operation_ids = orderline[key];
                for (var i, len = operation_ids.length; i<len; i++) {
                    var operation_id = operation_ids[i];
                    var operation = self.pos.db.get_operation_by_id(
                            product.product_tmpl_id,
                            operation_id
                    );
                    operations.push(operation);
                }
                product.operations = operations;
            }

            return product;
        },

    });
}
