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

        initialize: function (data) {
            this.collection.bind('reset', this.render, this);
            //this.listenTo(this.collection, 'reset', this.render);
            Backbone.on("EV_ImageSelected", this.chooseCookbooks, this);
            this.master = data.master;
        },

        render: function () {
            console.log("Rendering Cookbooks...");
            if (!this.collection.length) {
                this.$el.html("<option>No Cookbooks available</option>");
            } else {
                this.collection.sort();
                this.$el.html("");
                this.collection.each(function (cb) {
                    this.$el.append(new CookbookView({model: cb}).el);
                }, this);

            }
            return this;
        },
        toggleSelected: function (event) {
            var id = $(event.currentTarget).val();
            if (event) event.preventDefault();
            this.collection.deselectAll();
            id.forEach(function (i) {
                this.collection.select(this.collection.get(i));
            }, this);
            Backbone.trigger("EV_CookbookSelected", this.collection.selected);
        },

        chooseCookbooks: function (images) {
            var systems = _.pluck(_.pluck(images, "attributes"), "system");
            this.collection.reset(this.master.by_system(systems));
            
        },

    });
});