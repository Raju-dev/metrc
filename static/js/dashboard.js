odoo.define('metrc.dashboard', function (require) {
'use strict';

var ControlPanelMixin = require('web.ControlPanelMixin');
var core = require('web.core');
var Dialog = require('web.Dialog');
var Widget = require('web.Widget');
var ListView = require('web.ListView'); 
var ListController = require("web.ListController");

var local_storage = require('web.local_storage');

var _t = core._t;
var QWeb = core.qweb;

var includeDict = {
    renderButtons: function () {
        this._super.apply(this, arguments);
        if (this.modelName === "metrc.plants") {
            var your_btn = this.$buttons.find('button.o_button_help')                
            your_btn.on('click', this.proxy('o_button_help'))
        }
    },
    o_button_help: function(ev){
        ev.preventDefault();

        var self = this;
        self.dialog = new Dialog(this, {
            size: 'large',
            title: _t('Sync Metrc Data'),
            $content: QWeb.render('metrc.add_plant_screen', { widget: self }),
            buttons: [
                {
                    text: _t("Save"),
                    classes: 'btn-primary',
                    close: false,
                    click: function(event) {
                        $('.create-plant-form').submit();
                    }
                },
                {
                    text: _t("Cancel"),
                    close: true,
                },
            ],
        }).open();
        self.dialog.opened(function() {
            $('#select-location').select2({
                placeholder: 'Select Location',
                ajax: {
                    url: '/get-different-locations',
                    dataType: 'json',
                    data: function (term, page) {
                        return {
                            q: term
                        }
                    },
                    processResults: function (data) {
                      // Transforms the top-level key of the response object from 'items' to 'results'
                      return {
                        results: data
                      };
                    },
                    results: function(data) {
                        return {
                            results: data.result
                        }
                    }
                }
            });

            $('#select-location').on('change', function(event) {
                $('input[name=location]').val(event.target.value);
                $('.create-plant-form').valid();
            });

            $('#select-room').select2({
                placeholder: 'Select Location',
                ajax: {
                    url: '/get-different-rooms',
                    dataType: 'json',
                    data: function (term, page) {
                        return {
                            q: term
                        }
                    },
                    processResults: function (data) {
                      // Transforms the top-level key of the response object from 'items' to 'results'
                      return {
                        results: data
                      };
                    },
                    results: function(data) {
                        return {
                            results: data.result
                        }
                    }
                }
            });

            $('#select-room').on('change', function(event) {
                $('input[name=room]').val(event.target.value);
                $('.create-plant-form').valid();
            });

            $('#select-strain').select2({
                placeholder: 'Select Location',
                ajax: {
                    url: '/get-different-strains',
                    dataType: 'json',
                    data: function (term, page) {
                        return {
                            q: term
                        }
                    },
                    processResults: function (data) {
                      // Transforms the top-level key of the response object from 'items' to 'results'
                      return {
                        results: data
                      };
                    },
                    results: function(data) {
                        return {
                            results: data.result
                        }
                    }
                }
            });

            $('#select-strain').on('change', function(event) {
                $('input[name=strain]').val(event.target.value);
                $('.create-plant-form').valid();
            });

            $('.create-plant-form').validate({
                ignore: '.ignore',
                rules: {
                    label: {
                        required: true
                    },
                    batch_name: {
                        required: true
                    },
                    batch_type: {
                        required: true
                    },
                    growth_phase: {
                        required: true
                    },
                    location: {
                        required: true
                    },
                    room: {
                        required: true
                    },
                    plant_count: {
                        required: true,
                        number: true
                    },
                    strain: {
                        required: true
                    },
                    planting_date: {
                        required: true
                    }
                },
                submitHandler: function() {
                    self._rpc({
                        route: '/create-plants',
                        params: {
                            label: $('input[name=label]').val(),
                            batch_name: $('input[name=batch_name]').val(),
                            batch_type: $('select[name=batch_type]').val(),
                            growth_phase: $('select[name=growth_phase]').val(),
                            location: $('input[name=location]').val(),
                            room: $('input[name=room]').val(),
                            plant_count: $('input[name=plant_count]').val(),
                            strain: $('input[name=strain]').val(),
                            planting_date: $('input[name=planting_date]').val()
                        }
                    })
                    .then(function(response) {
                        response = JSON.parse(response);
                        console.log(response);
                    });
                    return false;
                }
            });
        });
    }
};

ListController.include(includeDict); 

var Dashboard = Widget.extend(ControlPanelMixin, {
    template: 'metrc.dashboard_main',
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
            this.$searchview = $(QWeb.render("metrc.right_part", {
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

            if(!backend_response.status) {
                $('.o_buttons').html(
                    `
                        <h3>You haven't synced your Metrc data yet. Please sync in order to start using Metrc.</h3>
                        <button class="btn btn-sm btn-primary js_sync_metrc_button center-block mb8">Sync Now</button>
                    `
                );
            } else if(backend_response.status == 'sent') {
                 $('.o_buttons').html(
                     `
                         <h3>You haven't synced your Metrc data yet. Please sync in order to start using Metrc.</h3>
                         <button class="btn btn-sm btn-primary js_sync_metrc_button center-block mb8"><div class="wrapper-div"><div class="loader-small"></div></div>Syncing</button>
                     `
                 );
                 self.listen_to_changes()
            } else {
                 $('.o_buttons').html(
                     `
                        <p><label>Metrc API Key:</label> ${backend_response.metrc_api_key}</p>
                        <p><label>Metrc User Key:</label> ${backend_response.metrc_user_key}</p>
                        <p><label>Metrc License:</label> ${backend_response.metrc_license}</p>                                           
                        <button class="btn btn-sm btn-primary js_sync_metrc_button center-block mb8">Sync Again</button>
                     `  
                 );
            }
        });
    },
    listen_to_changes: function() {
        console.log('listen to changes')
        var self = this;
        var interval = setInterval(function() {
            self._rpc({
                route: '/sync-metrc-status'
            }).then(function (response) {
                var response = JSON.parse(response)
                if(response.status == 'synced') {
                    $('.o_buttons').html(
                     `
                            <p><label>Metrc API Key:</label> ${response.metrc_api_key}</p>
                            <p><label>Metrc User Key:</label> ${response.metrc_user_key}</p>
                            <p><label>Metrc License:</label> ${response.metrc_license}</p>                                           
                            <button class="btn btn-sm btn-primary js_sync_metrc_button center-block mb8">Sync Again</button>
                         `  
                     );       
                }     
            })
        }, 10000);
    },
    on_link_analytics_settings: function(ev) {
        ev.preventDefault();

        var self = this;
        self.dialog = new Dialog(this, {
            size: 'medium',
            title: _t('Sync Metrc Data'),
            $content: QWeb.render('metrc.sync_dialog_content', { widget: self }),
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
        self.dialog.opened(function() {
            self._rpc({
                route: '/sync-metrc-status'
            }).then(function (response) {
                response = JSON.parse(response)
                $('input[name=metrc_api_key]').val(response.metrc_api_key)
                $('input[name=metrc_user_key]').val(response.metrc_user_key)
                $('input[name=metrc_license]').val(response.metrc_license)
            })
        });
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
            self.listen_to_changes()
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

var PlantBatches = Widget.extend(ControlPanelMixin, {
    template: 'metrc.plant_batches',
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
            this.$searchview = $(QWeb.render("metrc.right_part", {
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
        var self = this;
        $(document).on('click', '.check-batch', function( event ) {
            if($(event.target).prop('checked')) {
                $('.check-batch').not($(event.target)).each(function(element, index) {
                    $(this).prop('checked', false);
                });
            }
        });
        setTimeout(function() {
            // $('a[data-toggle="tab"]').on( 'shown.bs.tab', function (e) {
            //     $.fn.dataTable.tables( {visible: true, api: true} ).columns.adjust();
            // });
            self.table = $('table.table').DataTable({
                ajax: window.location.origin+'/get-different-batches',
                scrollCollapse: true,
                paging: true,
                serverSide: true,
                dom: 'lBfrtip',
                "columnDefs": [ {
                    "targets": 0,
                    "render": function ( data, type, row, meta ) {
                      return `<input type="checkbox" class="check-batch" data-name="${row[1]}" data-growth-phase="Flowering" />`;
                    }
                }],
                buttons: [
                    {
                        text: 'Change Growth Phase',
                        className: 'btn btn-primary change-growth-button',
                        action: function( e, dt, node, config ) {
                            if(!$('.check-batch:checked').length) {
                                alert('Please select a bath to change growth phase');
                                return;
                            }

                            self.dialog = new Dialog(this, {
                                size: 'large',
                                title: _t('Change growth phase'),
                                $content: QWeb.render('metrc.change_growth_phase', { widget: self }),
                                buttons: [
                                    {
                                        text: _t("Save"),
                                        classes: 'btn-primary',
                                        close: false,
                                        click: function(event) {
                                            $('.change-growth-form').submit();
                                        }
                                    },
                                    {
                                        text: _t("Cancel"),
                                        close: true,
                                    },
                                ],
                            }).open();
                            self.dialog.opened(function() {
                                $('#select-location').select2({
                                    placeholder: 'Select Location',
                                    ajax: {
                                        url: '/get-different-locations',
                                        dataType: 'json',
                                        data: function (term, page) {
                                            return {
                                                q: term
                                            }
                                        },
                                        processResults: function (data) {
                                          // Transforms the top-level key of the response object from 'items' to 'results'
                                          return {
                                            results: data
                                          };
                                        },
                                        results: function(data) {
                                            return {
                                                results: data.result
                                            }
                                        }
                                    }
                                });

                                $('#select-location').on('change', function(event) {
                                    $('input[name=location]').val(event.target.value);
                                    $('.change-growth-form').valid();
                                });

                                $('.change-growth-form').validate({
                                    ignore: '.ignore',
                                    rules: {
                                        starting_tag: {
                                            required: true
                                        },
                                        location: {
                                            required: true
                                        },
                                        plant_count: {
                                            required: true
                                        },
                                        planting_date: {
                                            required: true
                                        }
                                    },
                                    submitHandler: function() {
                                        $('.change-growth-button').prop('disabled', true)
                                        self._rpc({
                                            route: '/change-growth-phase',
                                            params: {
                                                name: $('.check-batch:checked').attr('data-name'),
                                                change_growth_phase: $('.check-batch:checked').attr('data-growth-phase'),
                                                starting_tag: $('input[name=starting_tag]').val(),
                                                location: $('input[name=location]').val(),
                                                count: $('input[name=plant_count]').val(),
                                                planting_date: $('input[name=planting_date]').val()
                                            }
                                        })
                                        .then(function(growth_response) {
                                            $('.change-growth-button').prop('disabled', false)
                                            growth_response = JSON.parse(growth_response)
                                            if(growth_response.status == 'success') {
                                                self.newdialog = new Dialog(self, {
                                                    size: 'large',
                                                    title: _t('Change growth phase'),
                                                    $content: QWeb.render('metrc.change_growth_success', { widget: self, tags: growth_response.tags.join(',') }),
                                                    buttons: [
                                                        {
                                                            text: _t("Ok"),
                                                            close: true,
                                                        },
                                                    ],
                                                }).open();
                                                self.table.ajax.reload();
                                                self.dialog.close();
                                            } else {
                                                if(Array.isArray(growth_response.error)) {
                                                    var messageHtml = '<div class="alert alert-danger"><ul>';
                                                    growth_response.error.forEach(function(singleMessage) {
                                                        messageHtml+=`<li>${singleMessage.message}</li>`;
                                                    })
                                                    messageHtml+='</ul></div>';
                                                    $('.message-div').html(
                                                        `
                                                            <div class="alert alert-danger">${messageHtml}</div>
                                                        `
                                                    );
                                                } else if(growth_response.error.Message) {
                                                    $('.message-div').html(
                                                        `
                                                            <div class="alert alert-danger">${growth_response.error.Message}</div>
                                                        `
                                                    );
                                                } else {
                                                    $('.message-div').html(
                                                        `
                                                            <div class="alert alert-danger">Something went wrong while processing your request. Please try again later!</div>
                                                        `
                                                    );
                                                }
                                            }
                                        });
                                        return false;
                                    }
                                });
                            });
                        }
                    },
                    {
                        text: 'Add',
                        className: 'btn btn-primary',
                        action: function ( e, dt, node, config ) {
                            self.dialog = new Dialog(this, {
                                size: 'large',
                                title: _t('Add Plant Batches'),
                                $content: QWeb.render('metrc.add_plant_batches', { widget: self }),
                                buttons: [
                                    {
                                        text: _t("Save"),
                                        classes: 'btn-primary plant-batches-save',
                                        close: false,
                                        click: function(event) {
                                            $('.create-plant-form').submit();
                                        }
                                    },
                                    {
                                        text: _t("Cancel"),
                                        close: true,
                                    },
                                ],
                            }).open();
                            self.dialog.opened(function() {
                                $('.plant-batches-save').prepend(`<div style="display:none;" class="loader-small loader-batches-create"></div>`);
                                $('#select-location').select2({
                                    placeholder: 'Select Location',
                                    ajax: {
                                        url: '/get-different-locations',
                                        dataType: 'json',
                                        data: function (term, page) {
                                            return {
                                                q: term
                                            }
                                        },
                                        processResults: function (data) {
                                          // Transforms the top-level key of the response object from 'items' to 'results'
                                          return {
                                            results: data
                                          };
                                        },
                                        results: function(data) {
                                            return {
                                                results: data.result
                                            }
                                        }
                                    }
                                });

                                $('#select-location').on('change', function(event) {
                                    $('input[name=location]').val(event.target.value);
                                    $('.create-plant-form').valid();
                                });

                                $('#select-room').select2({
                                    placeholder: 'Select Location',
                                    ajax: {
                                        url: '/get-different-rooms',
                                        dataType: 'json',
                                        data: function (term, page) {
                                            return {
                                                q: term
                                            }
                                        },
                                        processResults: function (data) {
                                          // Transforms the top-level key of the response object from 'items' to 'results'
                                          return {
                                            results: data
                                          };
                                        },
                                        results: function(data) {
                                            return {
                                                results: data.result
                                            }
                                        }
                                    }
                                });

                                $('#select-room').on('change', function(event) {
                                    $('input[name=room]').val(event.target.value);
                                    $('.create-plant-form').valid();
                                });

                                $('#select-strain').select2({
                                    placeholder: 'Select Location',
                                    ajax: {
                                        url: '/get-different-strains',
                                        dataType: 'json',
                                        data: function (term, page) {
                                            return {
                                                q: term
                                            }
                                        },
                                        processResults: function (data) {
                                          // Transforms the top-level key of the response object from 'items' to 'results'
                                          return {
                                            results: data
                                          };
                                        },
                                        results: function(data) {
                                            return {
                                                results: data.result
                                            }
                                        }
                                    }
                                });

                                $('#select-strain').on('change', function(event) {
                                    $('input[name=strain]').val(event.target.value);
                                    $('.create-plant-form').valid();
                                });

                                $('.create-plant-form').validate({
                                    ignore: '.ignore',
                                    rules: {
                                        batch_name: {
                                            required: true
                                        },
                                        batch_type: {
                                            required: true
                                        },
                                        location: {
                                            required: true
                                        },
                                        room: {
                                            required: true
                                        },
                                        plant_count: {
                                            required: true
                                        },
                                        strain: {
                                            required: true
                                        },
                                        planting_date: {
                                            required: true
                                        }
                                    },
                                    submitHandler: function() {
                                        $('.loader-batches-create').show();
                                        $('.plant-batches-save').prop('disabled', true);

                                        self._rpc({
                                            route: '/create-plant-batches',
                                            params: {
                                                batch_name: $('input[name=batch_name]').val(),
                                                batch_type: $('select[name=batch_type]').val(),
                                                location: $('input[name=location]').val(),
                                                room: $('input[name=room]').val(),
                                                plant_count: $('input[name=plant_count]').val(),
                                                strain: $('input[name=strain]').val(),
                                                planting_date: $('input[name=planting_date]').val()
                                            }
                                        })
                                        .then(function(response) {
                                            response = JSON.parse(response)
                                            console.log(response)
                                            if(response.status == 'success') {
                                                self.table.ajax.reload();
                                                self.dialog.close();
                                            } else {
                                                if(Array.isArray(response.error)) {
                                                    var messageHtml = '<div class="alert alert-danger"><ul>';
                                                    response.error.forEach(function(singleMessage) {
                                                        messageHtml+=`<li>${singleMessage.message}</li>`;
                                                    })
                                                    messageHtml+='</ul></div>';
                                                    $('.message-div').html(
                                                        `
                                                            <div class="alert alert-danger">${messageHtml}</div>
                                                        `
                                                    );

                                                } else if(response.error.Message) {
                                                    $('.message-div').html(
                                                        `
                                                            <div class="alert alert-danger">${response.error.Message}</div>
                                                        `
                                                    );
                                                } else {
                                                    $('.message-div').html(
                                                        `
                                                            <div class="alert alert-danger">Something went wrong while processing your request. Please try again later!</div>
                                                        `
                                                    );
                                                }
                                            }
                                            $('.loader-batches-create').hide();
                                            $('.plant-batches-save').prop('disabled', false);
                                        });
                                        return false;
                                    }
                                });
                            });
                        }
                    }
                ]
            });
        
            // Apply a search to the second table for the demo
            //$('#myTable2').DataTable().search( 'New York' ).draw();
        }, 500);
    }
});

var Plants = Widget.extend(ControlPanelMixin, {
    template: 'metrc.plants',
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
            this.$searchview = $(QWeb.render("metrc.right_part", {
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
        var self = this;
        $(document).on('click', '.check-batch', function( event ) {
            if($(event.target).prop('checked')) {
                $('.check-batch').not($(event.target)).each(function(element, index) {
                    $(this).prop('checked', false);
                });
            }
        });
        setTimeout(function() {
            // $('a[data-toggle="tab"]').on( 'shown.bs.tab', function (e) {
            //     $.fn.dataTable.tables( {visible: true, api: true} ).columns.adjust();
            // });
            self.table = $('table.table').DataTable({
                ajax: window.location.origin+'/get-different-plants',
                scrollCollapse: true,
                paging: true,
                serverSide: true,
                "columnDefs": [ {
                    "targets": 0,
                    "render": function ( data, type, row, meta ) {
                      return `<input type="checkbox" class="check-batch" data-name="${row[1]}" data-growth-phase="Flowering" />`;
                    }
                }]
            });
        
            // Apply a search to the second table for the demo
            //$('#myTable2').DataTable().search( 'New York' ).draw();
        }, 500);
    }
});

var Categories = Widget.extend(ControlPanelMixin, {
    template: 'metrc.categories',
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
            this.$searchview = $(QWeb.render("metrc.right_part", {
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
        var self = this;
        $(document).on('click', '.check-batch', function( event ) {
            if($(event.target).prop('checked')) {
                $('.check-batch').not($(event.target)).each(function(element, index) {
                    $(this).prop('checked', false);
                });
            }
        });
        setTimeout(function() {
            // $('a[data-toggle="tab"]').on( 'shown.bs.tab', function (e) {
            //     $.fn.dataTable.tables( {visible: true, api: true} ).columns.adjust();
            // });
            self.table = $('table.table').DataTable({
                ajax: window.location.origin+'/get-different-categories',
                scrollCollapse: true,
                paging: true,
                serverSide: true,
                "columnDefs": [ {
                    "targets": 0,
                    "render": function ( data, type, row, meta ) {
                      return `<input type="checkbox" class="check-batch" data-name="${row[1]}" data-growth-phase="Flowering" />`;
                    }
                }]
            });
        
            // Apply a search to the second table for the demo
            //$('#myTable2').DataTable().search( 'New York' ).draw();
        }, 500);
    }
});

core.action_registry.add('metrc_dashboard', Dashboard);
core.action_registry.add('metrc_metrc_plant_batches', PlantBatches);
core.action_registry.add('metrc_metrc_plants', Plants);
core.action_registry.add('metrc_metrc_categories', Categories);

return Dashboard;
});