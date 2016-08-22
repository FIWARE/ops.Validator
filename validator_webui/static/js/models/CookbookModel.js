/**
 * Created by pm.verdugo@dit.upm.es on 12/05/2016.
 */
define(function (require) {
    "use strict";
    var Backbone = require('backbone'),
        bbsel = require('bbselect'),
        notification = require('views/NotificationView'),
        config = require("config");

    return Backbone.Model.extend({
        url: config.api_url + '/cookbooks/',
        initialize: function () {
            Backbone.Select.Me.applyTo(this);
        },

        save_remote: function (credentials) {
            notification().render({text:"Retrieving cookbook..."});
            this.id = null;
            this.credentials = credentials;
            this.set('image', this.get('image_name'));
            this.set('recipe', this.get('recipe_name'));
            this.save(this.model, {
                success: function (model, response) {
                    notification().render({type:"success", text:"Cookbook successfully uploaded"});
                },
                error: function (model, response) {
                    console.log(response);
                    notification().render({type:"error", text:response.responseJSON || "Error downloading Cookbook"});
                }, 
                async: false,
            }, this);
            return this;
        },
    });
});
