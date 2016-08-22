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

        initialize: function () {
            //this.collection.bind('reset', this.render, this);
            Backbone.on("EV_CookbookSelected", this.chooseRecipes, this);
            // Backbone.on("EV_ImageSelected", this.chooseRecipes, this);
        },

        render: function () {
            console.log("Rendering Recipes...");
            if (!this.collection.length) {
                this.$el.html("<option>No Recipes Available</option>");
            } else {
                this.collection.sort();
                this.$el.empty();
                var container = document.createDocumentFragment();
                this.collection.each(function (rec) {
                    container.appendChild(new RecipeView({model: rec}).el);
                });
                this.$el.append(container);
            }
            return this;
        },

        toggleSelected: function (event) {
            var id = $(event.currentTarget).val();
            if (event) event.preventDefault();
            this.collection.get(id).select();
            // this.collection.deselectAll();
            // id.forEach(function (i) {
            //     this.collection.select(this.collection.get(i));
            // }, this);
        },
        chooseRecipes: function (cookbook) {
            var id = cookbook.id;
            this.collection.reset(this.collection.by_cb(id));
            this.render();
        },


    });
});