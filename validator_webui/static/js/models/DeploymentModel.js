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
                    self.dependencies();
                },
                error: function (model, response) {
                    self.set('launch', 'ERROR')
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
                    self.set('dependencies', model.get('dependencies'));
                    self.syntax();
                },
                error: function (model, response) {
                    self.set('dependencies', 'ERROR');
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
                    self.set('syntax', model.get('syntax'));
                    self.deploy();
                },
                error: function (model, response) {
                    self.set('syntax', 'ERROR');
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
                    self.set('deploy', model.get('deploy'));
                    self.set('ok', model.get('ok'));
                },
                error: function (model, response) {
                    self.set('deploy', 'ERROR');
                    self.set('ok', 'ERROR');
                },
                timeout: cfg.timeout
            });

        },
    });
});
