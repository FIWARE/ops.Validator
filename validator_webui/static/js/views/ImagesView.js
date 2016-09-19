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

        initialize: function (data) {
            //this.collection.bind('reset', this.render, this);
            Backbone.on("EV_CookbookSelected", this.chooseImages, this);
        },

        render: function () {
            console.log("Rendering Images...");
            if (!this.collection.length) {
                this.$el.html("<option>No Images Available</option>");
            } else {
                this.collection.sort();
                this.$el.empty();
                var container = document.createDocumentFragment();
                this.collection.each(function (image) {
                    container.appendChild(new ImageView({model: image}).el);
                }, this);
                this.$el.append(container);
            }
            return this;
        },

        toggleSelected: function (event) {
            var id = $(event.currentTarget).val();
            if (event) event.preventDefault();
            // this.collection.deselectAll();
            // id.forEach(function (i) {
            //     this.collection.get(i).select();
            // }, this);
            this.collection.get(id).select();
            // Backbone.trigger('EV_ImageSelected', this.collection.selected);
        },
        
        chooseImages: function (cookbook) {
            var system = cookbook.get('system');
            this.collection.reset(this.collection.by_system(system));
             this.render();
        },
    });
});