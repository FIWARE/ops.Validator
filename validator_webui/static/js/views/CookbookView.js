/**
 * Created by Administrator on 12/05/2016.
 */
define(function (require) {
    "use strict";
    var _ = require("underscore"),
        Backbone = require('backbone'),
        Cookbook = require('models/CookbookModel');

    return Backbone.View.extend({
        model: Cookbook,

        initialize: function () {
            this.template = _.template('<option value="<%=id%>"><%=system%>:<%= name %>:<%=version%></option>');
            this.render();
        },

        render: function () {
            this.setElement(this.template(this.model.attributes));
            return this;
        }
    })
});