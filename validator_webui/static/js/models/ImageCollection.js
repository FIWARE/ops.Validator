/**
 * Created by pm.verdugo@dit.upm.es on 12/05/2016.
 */
define(function (require) {

    "use strict";

    var Backbone = require('backbone'),
        config = require('config'),
        Image = require('models/ImageModel'),
        basicauth = require('bbbasicauth'),
        notification = require('views/NotificationView'),
        bbsel = require('bbselect');
    var $ = require("jquery");

    return Backbone.Collection.extend({
        url: config.api_url + '/images/',
        model: Image,
        sort_key: 'system',

        initialize: function (credentials, models, options) {
            if (credentials && !!credentials.username && !!credentials.password) {
                this.get_remote(credentials);
            }
            Backbone.Select.Many.applyTo(this, models, options);
        },

        comparator: function (item) {
            return item.get(this.sort_key);
        },

        get_remote: function (credentials) {
            console.log("Fetching Images...");
            notification().render({ text: 'Retrieving images...' });
            this.credentials = credentials;
            this.fetch({reset: true,
                success: function (model, response) {
                    notification().render({type:"success", text:"Images successfully retrieved"});
                },
                error: function (model, response) {
                    console.log(response);
                    notification().render({type:"error", text:"Error retrieving Images"});
                }
            });
        }
    });
});
