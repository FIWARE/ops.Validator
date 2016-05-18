/**
 * Created by Administrator on 12/05/2016.
 */
define(function (require) {
    "use strict";
    var _ = require("underscore"),
        Backbone = require('backbone'),
        CookBook = require('models/CookBookModel');
    return Backbone.View.extend({
            model: CookBook,
            tagName: 'li',
            template: '',

            initialize: function () {
                this.template = _.template('<option value="cookbooks/<%= id %>"><%= name %></option>');
            },
            render: function () {
                this.$el.html(this.template(this.model.attributes));
                return this;
            }
        })
});