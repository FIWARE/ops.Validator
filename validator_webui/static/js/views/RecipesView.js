/**
 * Created by Administrator on 18/05/2016.
 */
define(function (require) {
    "use strict";

    var Backbone = require('backbone'),
        RecipeView = require('views/RecipeView'),
        _ = require("underscore");

    return Backbone.View.extend({
        events: {
            "change": "toggleSelected"
        },
        el: "#sel_recipes",

        initialize: function (data) {
            this.collection.bind('reset', this.render, this);
            Backbone.on("EV_CookbookSelected", this.chooseRecipes, this);
            Backbone.on("EV_ImageSelected", this.chooseRecipes, this);
            this.master = data.master;
        },

        render: function () {
            console.log("Rendering Recipes...");
            if (!this.collection.length) {
                this.$el.html("<option>No Recipes Available</option>");
            } else {
            this.collection.sort();
            this.$el.html("");
            this.collection.each(function (recipe) {
                this.$el.append(new RecipeView({model: recipe}).el);
            }, this);
            }
            return this;
        },

        toggleSelected: function (event) {
            var id = $(event.currentTarget).val();
            if (event) event.preventDefault();
            this.collection.deselectAll();
            id.forEach(function(i){
                this.collection.select(this.collection.get(i));
            }, this);
        },

        chooseRecipes: function (cbs) {
            var ids = _.pluck(cbs, "id");
            this.collection.reset(this.master.by_cb(ids));
        },


    });
});