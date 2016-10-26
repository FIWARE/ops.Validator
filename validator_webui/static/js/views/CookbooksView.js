/**
 * Created by Administrator on 18/05/2016.
 */
define(function (require) {
    "use strict";

    var Backbone = require('backbone'),
        CookbookView = require('views/CookbookView'),
        _ = require("underscore");

    return Backbone.View.extend({
        events: {
            "change": "toggleSelected"
        },
        el: "#sel_cookbooks",

        initialize: function () {
            this.collection.bind('reset', this.render, this);
        },

        render: function () {
            console.log("Rendering Cookbooks...");
            if (!this.collection.length) {
                this.$el.html("<option>No Cookbooks available</option>");
            } else {
                this.collection.sort();
                this.$el.empty();
                var container = document.createDocumentFragment();
                this.collection.each(function (cb) {
                    container.appendChild(new CookbookView({model: cb}).el);
                }, this);
                this.$el.append(container);
            }
            return this;
        },
        toggleSelected: function (event) {
            var id = $(event.currentTarget).val();
            if (event) event.preventDefault();
            this.collection.get(id).toggleSelected();
            Backbone.trigger("EV_CookbookSelected", this.collection.selected);
        },

    });
});