/**
 * Created by Administrator on 18/05/2016.
 */
define(function (require) {
    "use strict";

    var Backbone = require('backbone'),
        DeploymentView = require('views/DeploymentView');

    return Backbone.View.extend({
        el: "#table_deployments",
        tagName: 'tbody',

        initialize: function () {
            this.collection.bind('reset', this.render, this);
        },

        render: function () {
            console.log("Rendering Deployments...");
            console.log(this.collection);
            this.$el.html("");
            this.collection.each(function (deployment) {
                this.$el.append(new DeploymentView({model: deployment}).el);
            }, this);
            return this;
        },

    });
});