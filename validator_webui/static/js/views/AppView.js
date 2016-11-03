/**
 * Created by Administrator on 02/06/2016.
 */
define(function (require) {
    "use strict";

    var Backbone = require('backbone'),
        notification = require("views/NotificationView"),
        RecipesView = require("views/RecipesView"),
        ImagesView = require("views/ImagesView"),
        DeploymentsView = require("views/DeploymentsView"),
        CookbooksView = require("views/CookbooksView"),
        ResultsView = require("views/ResultsView"),
        RecipeCollection = require("models/RecipeCollection"),
        CookbookCollection = require("models/CookbookCollection"),
        ImageCollection = require("models/ImageCollection"),
        DeploymentCollection = require("models/DeploymentCollection"),
        DeploymentModel = require("models/DeploymentModel"),
        $ = require("jquery"),
        CookbookModel = require("models/CookbookModel"),
        config = require("config");

    return Backbone.View.extend({

        el: $("#validator_app"),

        events: {
            "click #button_upload": "upload_cookbook",
            "click #button_github": "upload_github",
            // "click #button_refresh_local": "refresh_local_recipes",
            "click #button_add": "add_to_deployments",
            "click #button_run": "run_deployments",
            "change #sel_cookbooks": "validate",
            "change #sel_recipes ": "validate",
            "change #sel_images": "validate",
            "change #username": "render",
            "change #password": "render",
        },

        initialize: function () {
            console.log("Booting...")
            this.cookbookssel = new CookbooksView({collection: new CookbookCollection()});
            this.recipessel = new RecipesView({collection: new RecipeCollection(), master: new RecipeCollection()});
            this.imagessel = new ImagesView({collection: new ImageCollection()});
            this.deploymentsview = new DeploymentsView({collection: new DeploymentCollection()});
            this.resultsview = new ResultsView({collection: new DeploymentCollection()});
            notification().render({text: 'Please insert your FIWARE Lab credentials'});
            // debug mode
            if(config.debug)           
                this.set_values();
            this.render();
        },

        render: function () {
            var creds = this.get_credentials();
            this.cookbookssel.collection.get_remote(creds);
            this.recipessel.collection.get_remote(creds);
            this.recipessel.master.get_remote(creds);
            this.imagessel.collection.get_remote(creds);

        },

        get_credentials: function () {
            return {
                username: this.$("#username").val(),
                password: this.$("#password").val()
            }
        },
        set_values: function () {
            this.$("#username").val(config.username);
            this.$("#password").val(config.password);
            this.$("#upload_url").val(config.upload_url);

        },

        add_to_deployments: function () {
            var d = new DeploymentModel({
                cookbook: this.cookbookssel.collection.selected.get('name'),
                recipe_name: this.recipessel.master.selected.get('name'),
                image_name: this.imagessel.collection.selected.get('tag'),
                system: this.imagessel.collection.selected.get('system')
            });
            this.deploymentsview.collection.add(d);
            this.deploymentsview.render();
        },

        run_deployments: function () {
            this.resultsview.collection.reset();
            this.deploymentsview.collection.each(function (d) {
                this.resultsview.collection.add(d);
                d.save_remote(this.get_credentials());
            }, this);
            $('#button_github').removeAttr('disabled');
        },

        upload_cookbook: function () {
            var cb = new CookbookModel({
                upload_url: this.$("#upload_url").val()
            });
            cb.save_remote(this.get_credentials());
            this.render();
        },
        
        upload_github: function () {
            this.deploymentsview.collection.each(function (d) {
              d.cookbook.upload_github();  
            })
        },
        
        validate: function () {
            if (!this.cookbookssel.collection.selected || !this.imagessel.collection.selected || !this.recipessel.master.selected) {
                $('#button_add').attr('disabled', 'disabled');

            } else {
                $('#button_add').removeAttr('disabled');
            }
        },
    });
});