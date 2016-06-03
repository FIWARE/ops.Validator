/**
 * Created by Administrator on 12/05/2016.
 */
define(function (require) {
    "use strict";
    var _ = require("underscore"),
        Backbone = require('backbone'),
        Deployment = require('models/DeploymentModel');

    return Backbone.View.extend({
        model: Deployment,
        tagName: 'tr',
        template: '',
        events: {
            "click .remove-btn": "delete"
          },
        initialize: function () {
            this.template = _.template('<td><%=image%></td><td><%=cookbook%></td><td><%=recipe%></td><td><button class="remove-btn">Remove</button></td>');
            this.render();
        },

        render: function () {
            this.$el.html(this.template(this.model.attributes));
            return this;
        },
        delete: function(){
            console.log("Removing item");
            this.remove();
            this.model.destroy();
        }
    })
});