/**
 * Created by Administrator on 12/05/2016.
 */
define(function (require) {
    "use strict";
    var _ = require("underscore"),
        Backbone = require('backbone'),
        Recipe = require('models/RecipeModel'),
        Cookbook = require('models/CookbookModel');

    return Backbone.View.extend({
            model: Recipe,
            tagName: 'tr',
            template: '',

            initialize: function () {
                this.template = _.template('<td><input type="checkbox"/></td><td>system1</td><td><%= cookbook %></td><td><%= name %></td>');
                this.render();
            },
        
            render: function () {
                var cb = new Cookbook();
                cb.fetch({url: this.model.get('cookbook'), async:false});
                this.model.set('cookbook', cb.get('name'));
                this.$el.html(this.template(this.model.attributes));
                return this;
            }
        })
});