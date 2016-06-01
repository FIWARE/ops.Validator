/**
 * Created by Administrator on 12/05/2016.
 */
define(function (require) {
    "use strict";
    var _ = require("underscore"),
        Backbone = require('backbone'),
        Recipe = require('models/RecipeModel');

    return Backbone.View.extend({
            model: Recipe,
            tagName: 'tr',
            template: '',

            initialize: function () {
                this.template = _.template('<td><input type="checkbox"/></td><td>system1</td><td><%= cookbook %></td><td><%= name %></td>');
                this.render();
            },
        
            render: function () {
                console.log(this.model.cookbook);
                this.$el.html(this.template(this.model.attributes));
                return this;
            }
        })
});