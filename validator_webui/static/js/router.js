/**
 * Created by Administrator on 18/05/2016.
 */
define(function (require) {
    "use strict";

    var Backbone = require('backbone'),
        RecipesView = require('views/RecipesView'),
        recipesModel = require('models/RecipesModel');

    return Backbone.Router.extend({
        routes: {
            "": "home",
        },

        home: function () {
            console.log("Booting...");
            var recipesCollection = new recipesModel();
            recipesCollection.fetch();
            var recipesRows = new RecipesView({collection: recipesCollection});
        },
    })
});
