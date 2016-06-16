/**
 * Created by Administrator on 18/05/2016.
 */
define(function (require) {
    "use strict";

    var Backbone = require('backbone'),
        ImageView = require('views/ImageView');

    return Backbone.View.extend({
        events: {
            "change": "toggleSelected"
        },

        el: "#sel_images",

        initialize: function () {
            this.collection.bind('reset', this.render, this);
        },

        render: function () {
            console.log("Rendering Images...");
            if (!this.collection.length) {
                this.$el.html("<option>No Images Available</option>");
            } else {
                this.collection.sort();
                this.$el.html("");
                this.collection.each(function (image) {
                    this.$el.append(new ImageView({model: image}).el);
                }, this);
            }
            return this;
        },

        toggleSelected: function (event) {
            var id = $(event.currentTarget).val();
            if (event) event.preventDefault();
            this.collection.deselectAll();
            id.forEach(function(i){
                this.collection.get(i).select();
            }, this);
            Backbone.trigger('EV_ImageSelected', this.collection.selected);
        },

    });
});