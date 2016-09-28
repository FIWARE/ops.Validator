/**
 * Created by Administrator on 28/09/2016.
 */
/**
 * Created by Administrator on 12/05/2016.
 */
define(function (require) {
    "use strict";
    var _ = require("underscore"),
        Backbone = require('backbone'),
        ModalView = require('bbmodaldialog'),
        Deployment = require('models/DeploymentModel');

    return Backbone.ModalView.extend({
        name: "LogView",
        model: Deployment,
        template: '',
        initialize: function () {
            this.template = _.template("<h2>Log View</h2><div class='logview'><%=log%></div>")
        },
        render: function (logconts) {
            this.$el.html(this.template({log: logconts}));
            return this;
        },
    })
});