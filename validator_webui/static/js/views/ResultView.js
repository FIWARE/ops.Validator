/**
 * Created by Administrator on 17/06/2016.
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
            this.model.bind('change', this.render);
            this.template = _.template(
                '<td><%=image%></td>' +
                '<td><%=cookbook%></td>' +
                '<td><%=recipe%></td>' +
                '<td><%=launch%></td>' +
                '<td><%=dependencies%></td>' +
                '<td><%=syntax%></td>' +
                '<td><%=deployment%></td>' +
                '<td><%=ok%></td>'
            );
            this.render();
        },

        render: function () {
            for (var k in this.model.attributes) {
                if (this.model.attributes[k] == null) {
                    this.model.attributes[k] = "NA"
                }
            }
            this.$el.html(this.template(this.model.attributes));
            //this.setElement(this.template(this.model.attributes));
            return this;
        },
        delete: function () {
            console.log("Removing item");
            this.remove();
            this.model.destroy();
        }
    })
});