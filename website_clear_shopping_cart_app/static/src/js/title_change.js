odoo.define("sc_login.title",function (require) {
    "use strict";
    
    var core = require('web.core');
    var WebClient =require('web.WebClient');
    var QWeb = core.qweb,
    _t = core._t;   

    WebClient.include({
        start: function() {
            this.set('title_part', {"zopenerp": "Silvercom"});
            return this._super();
            },
        });
});