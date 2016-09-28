/**
 * Created by Administrator on 17/06/2016.
 */
define(function (require) {
    "use strict";
    var _ = require("underscore"),
        Backbone = require('backbone'),
        Deployment = require('models/DeploymentModel'),
        LogView = require("views/LogView"),
        Image = require('models/ImageModel');

    return Backbone.View.extend({
        model: Deployment,
        tagName: 'tr',
        className: 'odd',
        template: _.template(
            '<td><%=image_name%></td>' +
            '<td><%=cookbook%></td>' +
            '<td><%=recipe_name%></td>' +
            '<td><%=launch_link%></td>' +
            '<td><%=dependencies_link%></td>' +
            '<td><%=syntax_link%></td>' +
            '<td><%=deployment_link%></td>'
        ),
        events: {
            "click .remove-btn": "delete",
            "click #launch_log": "show_launch_log",
            "click #dependencies_log": "show_dependencies_log",
            "click #syntax_log": "show_syntax_log",
            "click #deployment_log": "show_deployment_log",
        },
        initialize: function () {
            this.model.bind('change', this.render, this);
            this.render();
        },

        clean_view: function (att) {
            if (this.model.attributes[att] == null) {
                this.model.set(att + "_link", "NA")
            } else {
                this.model.set(att + "_link", "<a id='"+ att + "_log' href='#'>" + this.model.get(att) + "</a>")
            }
        },

        render: function () {
            this.clean_view("launch");
            this.clean_view("syntax");
            this.clean_view("dependencies");
            this.clean_view("deployment");
            this.$el.html(this.template(this.model.attributes));
            return this;
        },
        show_launch_log: function () {
            var log = new LogView();
            console.log(this.model.get("launch_log"));
            log.render(this.model.get("launch_log")).showModal({
                showCloseButton:true,
                closeImageUrl: "images/close-modal.png",
                css: {
                    "width": "500px",
                    "height": "500px",
                    "border": "2px solid #111",
                    "background-color": "#fff",
                    "-webkit-border-radius": "0",
                    "-moz-border-radius": "0",
                    "border-radius": "0"
                }
            });
        },
        show_dependencies_log: function () {
            var log = new LogView();
            log.render(this.model.get("dependencies_log")).showModal({
                closeImageUrl: "images/close-modal.png",
                css: {
                    "border": "2px solid #111",
                    "background-color": "#fff",
                    "-webkit-border-radius": "0",
                    "-moz-border-radius": "0",
                    "border-radius": "0"
                }
            });
        },
                show_syntax_log: function () {
            var log = new LogView();
            log.render(this.model.get("syntax_log")).showModal({
                closeImageUrl: "images/close-modal.png",
                css: {
                    "border": "2px solid #111",
                    "background-color": "#fff",
                    "-webkit-border-radius": "0",
                    "-moz-border-radius": "0",
                    "border-radius": "0"
                }
            });
        },
                show_deployment_log: function () {
            var log = new LogView();
            log.render(this.model.get("deployment_log")).showModal({
                closeImageUrl: "images/close-modal.png",
                css: {
                    "border": "2px solid #111",
                    "background-color": "#fff",
                    "-webkit-border-radius": "0",
                    "-moz-border-radius": "0",
                    "border-radius": "0"
                }
            });
        },
    })
});