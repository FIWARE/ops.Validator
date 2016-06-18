/**
 * Created by Administrator on 17/06/2016.
 */
define(function (require) {
    "use strict";
    var _ = require("underscore"),
        Backbone = require('backbone'),
        Deployment = require('models/DeploymentModel'),
        Image = require('models/ImageModel');

    return Backbone.View.extend({
        model: Deployment,
        tagName: 'tr',
        template: _.template(
            '<td><%=image_name%></td>' +
            '<td><%=cookbook%></td>' +
            '<td><%=recipe_name%></td>' +
            '<td><%=launch_link%></td>' +
            '<td><%=syntax_link%></td>' +
            '<td><%=dependencies_link%></td>' +
            '<td><%=deploy_link%></td>' +
            '<td><%=ok_link%></td>'
        ),
        events: {
            "click .remove-btn": "delete"
        },
        initialize: function () {
            this.model.bind('change', this.render, this);
            this.render();
        },

        clean_view: function (att) {
            if (this.model.attributes[att] == null) {
                this.model.set(att + "_link", "NA")
            } else {
                this.model.set(att + "_link", "<a href='#'>" + this.model.get(att) + "</a>")
            }
        },

        render: function () {
            this.clean_view("launch");
            this.clean_view("dependencies");
            this.clean_view("syntax");
            this.clean_view("deploy");
            this.clean_view("ok");
            this.$el.html(this.template(this.model.attributes));
            //this.setElement(this.template(this.model.attributes));
            return this;
        },

    })
});