/**
 * Created by Administrator on 18/05/2016.
 */
define(function (require) {
    "use strict";

    var Backbone = require('backbone'),
        RecipeView = require('views/RecipeView');

    return Backbone.View.extend({

            el: "#table_recipes",

            initialize: function () {
                this.collection.bind('reset', this.render, this);
                this.listenTo(this.collection, 'reset', this.render);
            },

            render: function () {
                console.log("Rendering...");
                console.log(this.collection);
                this.collection.each(function (recipe) {
                    console.log(recipe);
                    this.$el.append(new RecipeView({model: recipe}).el);
                }, this);
                return this;
            }

        });
});