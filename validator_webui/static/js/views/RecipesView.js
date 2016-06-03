/**
 * Created by Administrator on 18/05/2016.
 */
define(function (require) {
    "use strict";

    var Backbone = require('backbone'),
        RecipeView = require('views/RecipeView');

    return Backbone.View.extend({
        events: {
            "change": "toggleSelected"
        },
        el: "#sel_recipes",

        initialize: function () {
            this.collection.bind('reset', this.render, this);
            //this.listenTo(this.collection, 'reset', this.render);
        },

        render: function () {
            console.log("Rendering Recipes...");
            this.collection.sort();
            this.collection.each(function (recipe) {
                this.$el.append(new RecipeView({model: recipe}).el);
            }, this);
            return this;
        },
        toggleSelected: function (event) {
            var id = $(event.currentTarget).val();
            if (event) event.preventDefault();
            this.collection.deselectAll();
            id.forEach(function(i){
                this.collection.get(i).select();
            }, this);
        },


    });
});