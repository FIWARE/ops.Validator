/**
 * Created by pm.verdugo@dit.upm.es on 12/05/2016.
 */
define(function (require) {
    "use strict";
    var Backbone = require('backbone');
    var cfg = require('config');
    return Backbone.Model.extend({
        save_remote: function (credentials) {
            this.id = null;
            this.credentials = credentials;
            this.set('image', this.get('image_name'));
            this.set('recipe', this.get('recipe_name'));
            this.save(this.model, {
                success: function (model, response) {
                    model.launch();
                },
                error: function (model, response) {
                    console.log(response);
                },
                timeout: cfg.timeout
            }, this);
            return this;
        },
        launch: function () {
            var self = this;
            console.log("Launching " + this.get("image_name"));
            var resp = Backbone.sync("launch", self, {
                type: 'PUT',
                url: this.url() + "/launch/",
                async: true,
                success: function (model, response) {
                    self.set('launch', model.launch);
                    self.set('launch_log', model.launch_log);
                    self.dependencies();
                },
                error: function (model, response) {
                    self.set('launch', 'ERROR')
                    self.set('launch_log', model.launch_log);
                },
                timeout: cfg.timeout
            });
            return this;
        },
        dependencies: function () {
            var self = this;
            console.log("Dependencies checking for " + this.get("recipe_name"));
            var resp = Backbone.sync("dependencies", self, {
                type: 'PUT',
                url: this.url() + "/dependencies/",
                async: true,
                success: function (model, response) {
                    self.set('dependencies', model.dependencies);
                    self.set('dependencies_log', model.dependencies_log);
                    self.syntax();
                },
                error: function (model, response) {
                    self.set('dependencies', 'ERROR');
                    self.set('dependencies_log', model.dependencies_log);
                    self.syntax();
                },
                timeout: cfg.timeout
            });
        },
        syntax: function () {
            var self = this;
            console.log("Syntax Checking for " + this.get("recipe_name"));
            var resp = Backbone.sync("syntax", self, {
                type: 'PUT', url: this.url() + "/syntax/", async: true,
                success: function (model, response) {
                    self.set('syntax', model.syntax);
                    self.set('syntax_log', model.syntax_log);
                    self.deploy();
                },
                error: function (model, response) {
                    self.set('syntax', 'ERROR');
                    self.set('syntax_log', model.syntax_log);
                    self.deploy();
                },
                timeout: cfg.timeout
            });
        },
        deploy: function () {
            var self = this;
            console.log("Deployment checking for " + this.get("recipe_name"));
            var resp = Backbone.sync("deploy", self, {
                type: 'PUT', url: this.url() + "/deploy/", async: true,
                success: function (model, response) {
                    self.set('deployment', model.deployment);
                    self.set('deployment_log', model.deployment_log);
                },
                error: function (model, response) {
                    self.set('deployment', 'ERROR');
                    self.set('deployment_log', model.deployment_log);
                },
                timeout: cfg.timeout
            });

        },
    });
});
