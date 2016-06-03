/**
 * Created by Administrator on 18/05/2016.
 */
define(function (require) {
    "use strict";

    var Backbone = require('backbone'),
        CookbookView = require('views/CookbookView');

    return Backbone.View.extend({
        events: {
            "change": "toggleSelected"
        },
        el: "#sel_cookbooks",

        initialize: function () {
            this.collection.bind('reset', this.render, this);
            //this.listenTo(this.collection, 'reset', this.render);
        },

        render: function () {
            console.log("Rendering Cookbooks...");
            this.collection.sort();
            this.collection.each(function (cb) {
                this.$el.append(new CookbookView({model: cb}).el);
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