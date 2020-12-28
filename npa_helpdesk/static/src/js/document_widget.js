odoo.define('npa_helpdesk.npa_helpdesk',function (require) {
'use strict';

var registry = require('web.field_registry');
var core = require('web.core');
var basic_fields = require('web.basic_fields');
var DocumentViewer = require('npa_helpdesk.DocumentViewer');
var relational_fields = require('web.relational_fields');
var QWeb = core.qweb;
var _t = core._t;

    var QuickDocViewer = basic_fields.InputField.extend({
        className: 'btn-hover',
        events: _.extend({}, basic_fields.InputField.prototype.events, {
            'mouseover': '_onHoverDocViewer',
        }),
        supportedFieldTypes: ['char'],
        init: function () {
            this._super.apply(this, arguments);
            this.tagName = this.mode === 'readonly' ? 'a' : 'input';
        },
        getFocusableElement: function () {
            return this.mode === 'readonly' ? this.$el : this._super.apply(this, arguments);
        },
        _renderReadonly: function (ev) {
            var field_values = this.value;
            var inp = this.$el;
            var iod = this.res_id;
            inp.html('<button type="button" class="btn oe_highlight_cancel o_icon_button"><i class="fa fa-fw o_button_icon fa-search"></i></button>');
        },
        _onHoverDocViewer: function () {
            var iod = this.res_id;
            this.$el.parent().popover({
                'content': function(e){
                    return '<img style="max-width:276px;max-height:276px;" src="'+'/web/binary/download_document/' + iod+'" class="img-responsive" />'
                },
                'html': true,
                'placement':  function(c,s){
                    return $(s).position().top < 200 ? 'left':'top'
                },
                'trigger': 'hover',
            });
        },
    });

    var LocationFieldUrl = basic_fields.InputField.extend({
        className: 'o_field_url',
        supportedFieldTypes: ['char'],
        init: function () {
            this._super.apply(this, arguments);
            this.tagName = this.mode === 'readonly' ? 'a' : 'input';
        },
        getFocusableElement: function () {
            return this.mode === 'readonly' ? this.$el : this._super.apply(this, arguments);
        },
        _renderReadonly: function() {
            var tmp = window.location.origin + '/web/binary/document_location?file_loc=' + this.value;
            this.$el.attr('href', tmp);
            this.$el.attr('target','_blank');
            this.$el.text(this.value);
        },
    });

    var DocumentFieldUrl = basic_fields.InputField.extend({
        className: 'o_field_url',
        supportedFieldTypes: ['char'],
        init: function () {
            this._super.apply(this, arguments);
            this.tagName = this.mode === 'readonly' ? 'a' : 'input';
        },
        getFocusableElement: function () {
            return this.mode === 'readonly' ? this.$el : this._super.apply(this, arguments);
        },
        _renderReadonly: function() {
            var tmp = window.location.origin + '/web/binary/open_document?id=' + this.res_id;
            this.$el.attr('href', tmp);
            this.$el.attr('target','_blank');
            this.$el.text(this.value);
        },
    });

    //one2many doc viewer
    var One2manyViewer = relational_fields.FieldOne2Many.extend({
        className: 'x2many-table',
        events: _.extend({}, relational_fields.FieldOne2Many.prototype.events, {
            'click .documents_viewer': '_onInputClickViewer',
        }),
        init: function () {
            this._super.apply(this, arguments);
            this.attach_list = [];
            this.ramci_list = [];
            this.cash_acct_list = [];
            this.contra_acct_list = [];
            this.margin_acct_list = [];
            var self = this;
            if (this.model === "res.partner" && this.name === "document_ids") {
                this.recordData.document_ids.data.forEach(function(value){
                    self.attach_list.push(value.data);
                    value.data['approval'] = true;
                })
            }           
        },
        _onOpenRecord: function (ev) {
            // we don't want interference with the components upstream.
            var self = this;
            var id = ev.data.id;
            var onSaved = function (record) {
                if (_.some(self.value.data, {id: record.id})) {
                    // the record already exists in the relation, so trigger an
                    // empty 'UPDATE' operation when the user clicks on 'Save' in
                    // the dialog, to notify the main record that a subrecord of
                    // this relational field has changed (those changes will be
                    // already stored on that subrecord, thanks to the 'Save').
                    self._setValue({ operation: 'UPDATE', id: record.id });
                } else {
                    // the record isn't in the relation yet, so add it ; this can
                    // happen if the user clicks on 'Save & New' in the dialog (the
                    // opened record will be updated, and other records will be
                    // created)
                    self._setValue({ operation: 'ADD', id: record.id });
                }
            };
            if ($(ev.data.target).hasClass('documents_viewer')){

            } else {
                this._openFormDialog({
                    id: id,
                    on_saved: onSaved,
                    on_remove: function () {
                        self._setValue({operation: 'DELETE', ids: [id]});
                    },
                    deletable: this.activeActions.delete,
                    readonly: this.mode === 'readonly',
                });
            }
            ev.stopPropagation();
        },
        _onInputClickViewer: function (event) {
            var self = this;
            event.stopImmediatePropagation();
            event.preventDefault();
            var attachmentName = event.currentTarget.outerText;
            var attachmentID = ''
            if (this.model === "res.partner" && this.name === "document_ids" && this.attach_list) {
                for (var i = 0 ; i < this.attach_list.length; i++) {
                    if (this.attach_list[i]['name'] == attachmentName){
                        attachmentID = this.attach_list[i]['id'];
                    }
                }
                var attachmentViewer = new DocumentViewer(this, this.attach_list, attachmentID);
                attachmentViewer.appendTo($('body'));
            } 
        },
    });

    // Doc Viewer 

    var LinkDocViewer = basic_fields.InputField.extend({
        className: 'oe_form_field_url',
        events: _.extend({}, basic_fields.InputField.prototype.events, {
            'click': '_onClick',
        }),
        supportedFieldTypes: ['char'],
        init: function () {
            this._super.apply(this, arguments);
            this.tagName = this.mode === 'readonly' ? 'a' : 'input';
        },
        getFocusableElement: function () {
            return this.mode === 'readonly' ? this.$el : this._super.apply(this, arguments);
        },
        _renderReadonly: function (ev) {
            var field_values = this.value;
            var inp = this.$el;
            var iod = this.res_id;
            this.$el.popover({
                'content': function(e){
                    return '<img style="max-width:276px;max-height:276px;" src="'+'/web/binary/download_document/' + iod+'" class="img-responsive" />'
                },
                'html': true,
                'placement':  function(c,s){
                    return $(s).position().top < 200 ? 'left':'top'
                },
                'trigger': 'hover',
            });
            inp.text(this.value);
        },
        _onClick: function (ev) {
            ev.stopPropagation();
            if (!this.value) {
                this.do_warn(_t("Resource Error"), _t("This resource is empty"));
            }
            var activeAttachmentID = this.res_id;
            if (activeAttachmentID) {
                var attachmentViewer = new DocumentViewer(this, [this.recordData], activeAttachmentID);
                attachmentViewer.appendTo($('body'));
            }
        },
    });


    basic_fields.FieldBinaryFile.include({
        init: function (parent, name, record) {
            this._super.apply(this, arguments);
            if (this.model && this.model == 'npa.document'){
                this.max_upload_size = 10 * 1024 * 1024; // Change Default Upload Max Size 25 to 10 MB.
            }
        },
    });

    registry.add('doc_url', LinkDocViewer);
    registry.add('one2many_document_list',One2manyViewer);
    registry.add('quick_doc_viewer',QuickDocViewer);
    registry.add('document_url',DocumentFieldUrl);
    registry.add('location_url', LocationFieldUrl);

    return {
        LinkDocViewer:LinkDocViewer,
        DocumentFieldUrl:DocumentFieldUrl,
        One2manyViewer:One2manyViewer,
        QuickDocViewer:QuickDocViewer,
        LocationFieldUrl:LocationFieldUrl
    }

});
