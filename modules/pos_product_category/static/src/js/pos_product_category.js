openerp.pos_product_category = function(instance, local) {
    module = instance.point_of_sale;
    var _t = instance.web._t;
    var round_pr = instance.web.round_precision;

    module.PosModel = module.PosModel.extend({

        initialize: function(session, attributes) {

            for (var i = 0 ; i < this.models.length; i++){
                if (this.models[i].model == 'pos.category') {
                    this.models[i].model = 'product.category';
                }
            }
            return this._super(session, attributes);
        }
   });
};
