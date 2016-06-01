/**
 * Created by Administrator on 18/05/2016.
 */
define(function (require) {
    "use strict";

    var Backbone = require('backbone'),
        RecipesView = require('views/RecipesView'),
        RecipesCollection = require('models/RecipeCollection');

    return Backbone.Router.extend({
        routes: {
            "": "home",
        },

        home: function () {
            console.log("Booting...");
            var recipesCollection = new RecipesCollection();
            var recipesRows = new RecipesView({collection: recipesCollection});
        },
    })
});
