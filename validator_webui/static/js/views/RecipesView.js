/**
 * Created by Administrator on 18/05/2016.
 */
define(function (require) {
    "use strict";

    var Backbone = require('backbone'),
        RecipeView = require('views/RecipeView'),
        RecipesView = Backbone.View.extend({

            el: "#table_recipes",
            //tagname: "tbody",

            initialize: function () {
                console.log(this.collection);
                this.render();
            },

            render: function () {
                this.collection.each(function (recipe) {
                    var recipeView = new RecipeView({model: recipe});
                    this.$el.append(recipeView.el);
                }, this);
            }

        });
    return RecipesView;
});