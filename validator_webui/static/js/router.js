/**
 * Created by Administrator on 18/05/2016.
 */
define(function (require) {
    "use strict";

    var Backbone = require('backbone'),
        RecipesView = require('views/RecipesView'),
        RecipesModel = require('models/RecipesModel');

    return Backbone.Router.extend({
        routes: {
            "": "home",
        },

        home: function () {
            console.log("Booting...");
            var recipesCollection = new RecipesModel();
            var recipesRows = new RecipesView({collection: recipesCollection});
        },
    })
});
