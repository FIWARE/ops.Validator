/**
 * Created by Administrator on 17/06/2016.
 */
define(function (require) {
    "use strict";

    var Backbone = require('backbone'),
        ResultView = require('views/ResultView');

    return Backbone.View.extend({
        el: "#table_results",
        tagName: 'tbody',

        initialize: function () {
            this.collection.bind('reset', this.render, this);
            this.collection.bind('add', this.render, this);
            this.render();
        },

        render: function () {
            console.log("Rendering Results...");
            if (!this.collection.length) {
                this.$el.html(
                    "<tr class='odd'>" +
                    "<td>No Image Selected</td>" +
                    "<td>No Cookbook Selected</td>" +
                    "<td>No Recipe Selected</td>" +
                    "<td>NA</td>" +
                    "<td>NA</td>" +
                    "<td>NA</td>" +
                    "<td>NA</td>" +
                    "</tr>"
                );
            } else {
                this.$el.empty();
                var container = document.createDocumentFragment();
                this.collection.each(function (result) {
                    container.appendChild(new ResultView({model: result}).el);
                }, this);
                this.$el.append(container);
            }
            return this;
        },

    });
});