/**
 * Created by pm.verdugo@dit.upm.es on 12/05/2016.
 */
define(function (require) {
    "use strict";
    var Backbone = require('backbone');
    return Backbone.Model.extend({
        save_remote: function (credentials) {
            this.id = null;
            this.credentials = credentials;
            this.save(this.model, {
                async: false,
                success: function (model, response) {
                },
                error: function (model, response) {
                    alert('wrong');
                    console.log(response);
                }
            });
            return this;
        },
        launch: function(){
            console.log("Launching "+this.get("recipe"));
            var resp = Backbone.sync("launch", this, {type: 'PUT', url: this.url()+"/launch/", async: false});
            this.set("launch", resp.responseJSON.launch);
        },
        syntax: function(){
            console.log("Syntax Checking for "+this.get("recipe"));
            Backbone.sync("syntax", this, {type: 'PUT', url: this.url()+"/syntax/", async: false});
        },
        dependencies: function(){
            console.log("Dependencies checking for "+this.get("recipe"));
            Backbone.sync("dependencies", this, {type: 'PUT', url: this.url()+"/dependencies/", async: false});
        },
        deployment: function(){
            console.log("Deployment checking for "+this.get("recipe"));
            Backbone.sync("deployment", this, {type: 'PUT', url: this.url()+"/deployment/", async: false});
        },
    });
});
