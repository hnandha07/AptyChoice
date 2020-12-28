odoo.define('npa_base.hide', function(require) {
    "use strict";

    var ListView = require('web.ListView');
    var SearchView = require('web.SearchView');
    var Menu = require('web.Menu');
    var UserMenu = require('web.UserMenu');
    var WebClient =require('web.WebClient');
    var Dialog = require('web.Dialog');
    var core = require('web.core');
    var Sidebar = require('web.Sidebar');
    var session = require("web.session");
    var QWeb = core.qweb,
    _t = core._t;

    ListView.include({
        init: function () {
            this._super.apply(this, arguments);
            this.controllerParams.importEnabled = false;
            if ((this.loadParams.context) && ('hide_checkboxes_treeview' in this.loadParams.context)) {
                this.rendererParams.hasSelectors =false;
            }
        },
    });

    Dialog.include({
        open: function(options) {
            var self = this;
            this.title = this.title.replace('Odoo', 'Silvercom')
            return this._super.apply(this, arguments);
        },
    });

    // Menu.include({
    //     _updateMenuBrand: function(brandName) {
    //         var session = this.getSession();
    //         this._super.apply(this, arguments);
    //         if (brandName) {
    //             this.$menu_brand_placeholder.text(String(session.brandName) + ' - ' + String(brandName)).show();
    //             this.$section_placeholder.show();
    //         } else {
    //             this.$menu_brand_placeholder.hide()
    //             this.$section_placeholder.hide();
    //         }
    //     },
    // }); 

    SearchView.include({
        init: function(parent, dataset, defaults, options) {
            if (options.action && ('hide_searchview' in options.action.context)) {
                options.action.flags.hasSearchView = false;
            }
            if (options.action && options.action.res_model && options.action.res_model.startsWith('npa.dashboard') || options.action && options.action.res_model &&  options.action.res_model.startsWith('npa.common_page'))
              {
                if (options.action && ('hide_controlpannel' in options.action.context)){
                    options.action.flags.headless = true;
                }else{
                    options.action.flags.headless = false;
                }
            }
            this._super(parent, dataset, defaults, options);
        },
    })   

    WebClient.include({
        start: function() {
            this.set('title_part', {"zopenerp": "Silvercom"});
            return this._super();
        },
    });

});
