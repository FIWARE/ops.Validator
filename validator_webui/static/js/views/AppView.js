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
        },

        initialize: function () {
            console.log("Booting...")
            this.cookbookssel = new CookbooksView({collection: new CookbookCollection()});
            this.imagessel = new ImagesView({collection: new ImageCollection()});
            this.recipessel = new RecipesView({collection: new RecipeCollection()});
            this.deploymentsview = new DeploymentsView({collection: new DeploymentCollection()});
            this.resultsview = new ResultsView({collection: new DeploymentCollection()});
            notification().render({text: 'Please insert your FIWARE Lab credentials'});
            // debug mode
            this.set_values();
            this.render();
        },

        render: function () {
            var creds = this.get_credentials();
            this.cookbookssel.collection.get_remote(creds);
            this.imagessel.collection.get_remote(creds);
            this.recipessel.collection.get_remote(creds);
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

        // refresh_remote_recipes: function () {
        //     var creds = this.get_credentials();
        //     new CookbookCollection().refresh(creds);
        //     var recipesRows = new RecipesView({collection: new RecipeCollection(creds)});
        //     this.render();
        // },
        //
        // refresh_local_recipes: function () {
        //     this.render();
        // },

        add_to_deployments: function () {
            // var self = this;
            // $.each(self.imagessel.collection.selected, function (key, image) {
            //     $.each(self.recipessel.collection.selected, function (key, recipe) {
            //         console.log("Creating new deployment");
            //         var d = new DeploymentModel({
            //             recipe_name: recipe.get('name'),
            //             image_name: image.get('tag'),
            //             cookbook: self.cookbookssel.collection.get(recipe.get('cookbook')).get('name'),
            //             system: image.get('system')
            //         });
            //         self.deploymentsview.collection.add(d);
            //     });
            // });
            var d = new DeploymentModel({
                cookbook: this.cookbookssel.collection.selected.get('name'),
                recipe_name: this.recipessel.collection.selected.get('name'),
                image_name: this.imagessel.collection.selected.get('tag'),
                system: this.imagessel.collection.selected.get('system')
            });
            this.deploymentsview.collection.add(d);
            this.deploymentsview.render();
        },

        run_deployments: function () {
            $('#button_github').removeAttr('disabled');
            this.resultsview.collection.reset();
            this.deploymentsview.collection.each(function (d) {
                this.resultsview.collection.add(d);
                d.save_remote(this.get_credentials());
            }, this);
            // this.resultsview.collection.each(function(d) {
            //    console.log("Generating " + d.get('recipe'));
            //    d.save_remote(this.get_credentials());
            // }, this);
            // this.resultsview.collection.each(function(r){
            //     r.launch();
            //     // r.syntax();
            //     // r.dependencies();
            //     // r.deployment();
            // }, this);
        },

        upload_cookbook: function () {
            var cb = new CookbookModel({
                upload_url: this.$("#upload_url").val()
            });
            cb.save_remote(this.get_credentials());
            this.cookbookssel.collection.get_remote(creds);
        },
        upload_github: function () {
            this.deploymentsview.collection.each(function (d) {
              d.cookbook.upload_github();  
            })
        },
        validate: function () {
            if (!this.cookbookssel.collection.selected || !this.imagessel.collection.selected || !this.recipessel.collection.selected) {
                $('#button_add').attr('disabled', 'disabled');

            } else {
                $('#button_add').removeAttr('disabled');
            }
        }
    });
});