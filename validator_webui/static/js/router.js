/**
 * Created by Administrator on 18/05/2016.
 */
define(function (require) {
    "use strict";
    var Backbone = require('backbone'),
        RecipesView = require('views/RecipesView'),
        SystemsView = require('views/SystemsView'),
        dummy = require('models/dummy');

    return Backbone.Router.extend({
        routes: {
            "": "home",
        },

        home: function () {
            var cbookList = new RecipesView({collection: dummy.cbCol});
            cbookList.render();
            var sysList = new SystemsView({collection: dummy.sysCol})
            sysList.render();
        },
    })
});
