/**
 * Created by Administrator on 02/06/2016.
 */

define(function (require) {
    "use strict";
    var Backbone = require('backbone'),
        config = require('config'),
        Cookbook = require('models/CookbookModel'),
        basicauth = require('bbbasicauth'),
        bbsel = require('bbselect');
    var $ = require("jquery");

    return Backbone.Collection.extend({
        url: config.api_url + '/cookbooks/',
        model: Cookbook,
        sort_key: 'name',
        initialize: function (credentials, models, options) {
            if (credentials) {
            this.get_remote(credentials);
                }
            Backbone.Select.Many.applyTo(this, models, options);
        },

        get_remote: function (credentials) {
            console.log("Fetching Cookbooks...");
            this.credentials = credentials;
            this.fetch({reset: true});
        },
        comparator: function(item) {
                return item.get(this.sort_key);
            },
        refresh: function (credentials) {
            this.credentials = credentials;
            console.log("Refreshing remote cookbooks");
            this.url = config.api_url + '/cookbooks/refresh/';
            this.fetch();
            console.log("Refreshing remote recipes");
            this.url = config.api_url + '/recipes/refresh/';
            this.fetch();
            this.url = config.api_url + '/cookbooks/';
        },
        by_system: function (syss) {
            return this.filter(function (rec) {
                return $.inArray(rec.get('system'), syss) > -1;
            });
        }
    });
});