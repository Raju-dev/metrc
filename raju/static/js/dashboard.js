odoo.define('raju.dashboard', function (require) {
'use strict';

var ajax = require('web.ajax');
var ControlPanelMixin = require('web.ControlPanelMixin');
var core = require('web.core');
var Dialog = require('web.Dialog');
var field_utils = require('web.field_utils');
var session = require('web.session');
var web_client = require('web.web_client');
var Widget = require('web.Widget');

var local_storage = require('web.local_storage');

var _t = core._t;
var QWeb = core.qweb;

var Dashboard = Widget.extend(ControlPanelMixin, {
    template: 'raju.dashboard_main',
    init: function (parent, object) {
        console.log('INIT!!!');
        this._super.apply(this, arguments);
    },
    start: function() {
    	this.update_cp();
    },
    events: {
        'click .js_sync_metrc_button': 'on_link_analytics_settings'
    },
    update_cp: function() {
        var self = this;
        if (!this.$searchview) {
            this.$searchview = $(QWeb.render("raju.right_part", {
                widget: this,
            }));
            this.$searchview.click('button.js_date_range', function(ev) {
                self.on_date_range_button($(ev.target).data('date'));
                $(this).find('button.js_date_range.active').removeClass('active');
                $(ev.target).addClass('active');
            });
        }
        this.update_control_panel({
            cp_content: {
                $searchview: this.$searchview,
            },
            breadcrumbs: this.getParent().get_breadcrumbs(),
        });
        this._rpc({
            route: '/sync-metrc-status'
        }).then(function (response) {
            var backend_response = JSON.parse(response);

            //if(!backend_response.status) {
                $('.o_buttons').html(
                    `
                        <h3>You haven't synced your Metrc data yet. Please sync in order to start using Metrc.</h3>
                        <button class="btn btn-sm btn-primary js_sync_metrc_button center-block mb8">Sync Now</button>
                    `
                );
            // } else if(backend_response.status == 'sent') {
            //     $('.o_buttons').html(
            //         `
            //             <h3>You haven't synced your Metrc data yet. Please sync in order to start using Metrc.</h3>
            //             <button class="btn btn-sm btn-primary js_sync_metrc_button center-block mb8"><div class="wrapper-div"><div class="loader-small"></div></div>Syncing</button>
            //         `
            //     );
            // }
        });
    },
    on_link_analytics_settings: function(ev) {
        ev.preventDefault();

        var self = this;
        self.dialog = new Dialog(this, {
            size: 'medium',
            title: _t('Sync Metrc Data'),
            $content: QWeb.render('raju.sync_dialog_content', { widget: self }),
            buttons: [
                {
                    text: _t("Save"),
                    classes: 'btn-primary',
                    close: false,
                    click: function(event) {
                        var metrc_api_key = self.dialog.$el.find('input[name="metrc_api_key"]').val();
                        var metrc_user_key = self.dialog.$el.find('input[name="metrc_user_key"]').val();
                        var metrc_license = self.dialog.$el.find('input[name="metrc_license"]').val();
                        $(".modal-footer").prepend(`
                            <div class="wrapper-div">
                                <div class="loader-small">
                                </div>
                            </div>
                        `);
                        if(event.target.tagName.toLowerCase() == 'button') {
                            $(event.target).prop('disabled', true);
                        } else {
                            $(event.target).parent().prop('disabled', true);
                        }
                        self.on_sync_metrc_data(metrc_api_key, metrc_user_key, metrc_license);
                    }
                },
                {
                    text: _t("Cancel"),
                    close: true,
                },
            ],
        }).open();
    },
    on_sync_metrc_data: function(metrc_api_key, metrc_user_key, metrc_license) {
        var self = this;
        return this._rpc({
            route: '/sync-metrc',
            params: {
                'metrc_api_key': metrc_api_key,
                'metrc_user_key': metrc_user_key,
                'metrc_license': metrc_license
            }
        }).then(function (response) {
            response = JSON.parse(response);
            if(response.status == 'success') {
                self.dialog.close();
                $('.js_sync_metrc_button').prop('disabled', true);
                $('.js_sync_metrc_button').html(`
                    <div class="wrapper-div"><div class="loader-small" style="display: none;"></div></div>Syncing
                `);
                $('.loader-small').show();
            } else {
                $('.text-message').html('The api keys are not valid!').css('color', '#dc3545').css('margin-top', '10px');
                $('.btn-primary').prop('disabled', false);
                $('.loader-small').hide();
            }
        });
    }
});

core.action_registry.add('raju_dashboard', Dashboard);
    return Dashboard;
});