/**
 * Created by Administrator on 12/05/2016.
 */
define(function (require) {
    "use strict";
    
    var _ = require("underscore"),
        Backbone = require('backbone'),
        System = require('models/SystemModel');

    return Backbone.View.extend({
        model: System,
        tagName: 'li',
        template: '',

        initialize: function () {
            this.template = _.template('<%= name %>');
        },
        render: function () {
            this.$el.html(this.template(this.model.attributes));
            return this;
        }
    })
});