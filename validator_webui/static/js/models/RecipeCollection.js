/**
 * Created by pm.verdugo@dit.upm.es on 12/05/2016.
 */
define(function (require) {

    "use strict";

    var Backbone = require('backbone'),
        config = require('config'),
        Recipe = require('models/RecipeModel'),
        basicauth = require('bbbasicauth'),
        bbsel = require('bbselect'),
        $ = require("jquery");

    return Backbone.Collection.extend({
        url: config.api_url + '/recipes/',
        model: Recipe,
        sort_key: 'name',

        initialize: function (credentials, models, options) {
            // if (credentials && !!credentials.username && !!credentials.password) {
            //     this.get_remote(credentials);
            // }
            Backbone.Select.One.applyTo(this, models, options);
        },
        comparator: function (item) {
            return item.get(this.sort_key);
        },
        get_remote: function (credentials) {
            console.log("Fetching Recipes...");
            this.credentials = credentials;
            this.fetch({reset: true});
        },
        by_cb: function (cbs) {
            return this.filter(function (rec) {
                return rec.get('cookbook') == cbs;
            });
        }
    });
});
