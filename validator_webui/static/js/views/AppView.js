/**
 * Created by Administrator on 02/06/2016.
 */
define(function (require) {
    "use strict";

    var Backbone = require('backbone'),
        RecipesView = require("views/RecipesView"),
        ImagesView = require("views/ImagesView"),
        DeploymentsView = require("views/DeploymentsView"),
        CookbooksView = require("views/CookbooksView"),
        RecipeCollection = require("models/RecipeCollection"),
        CookbookCollection = require("models/CookbookCollection"),
        ImageCollection = require("models/ImageCollection"),
        DeploymentCollection = require("models/DeploymentCollection"),
        DeploymentModel = require("models/DeploymentModel"),
        $ = require("jquery");

    return Backbone.View.extend({

        el: $("#validator_app"),

        events: {
            "click #button_refresh": "refresh_recipes",
            "click #button_add": "add_to_deployments",
            "click #button_run": "run_deployments",
        },

        initialize: function () {
            console.log("Booting...")
            this.username = this.$("#username");
            this.password = this.$("#password");
            this.render();
        },

        render: function () {
            this.imagescol = new ImageCollection(this.get_credentials());
            this.cookbookscol = new CookbookCollection();
            this.cookbooksmaster = new CookbookCollection(this.get_credentials());
            this.recipesmaster = new RecipeCollection(this.get_credentials());
            this.recipescol = new RecipeCollection();
            this.deploymentscol = new DeploymentCollection();
            this.imagessel = new ImagesView({collection: this.imagescol});
            this.cookbookssel = new CookbooksView({collection: this.cookbookscol, master: this.cookbooksmaster});
            this.recipessel = new RecipesView({collection: this.recipescol, master:this.recipesmaster});
            this.deploymentsview = new DeploymentsView({collection:this.deploymentscol});
        },

        get_credentials: function () {
            return {
                username: this.username.val(),
                password: this.password.val()
            }
        },

        refresh_recipes: function () {
            var creds = this.get_credentials();
            new CookbookCollection().refresh(creds);
            var recipesCollection = new RecipeCollection(creds);
            var recipesRows = new RecipesView({collection: recipesCollection});
        },

        add_to_deployments: function () {
            var self = this;
            $.each(self.imagessel.collection.selected, function (key, image) {
                $.each(self.recipessel.collection.selected, function (key, recipe) {
                    console.log("Creating new deployment");
                    var d = new DeploymentModel({
                        recipe: recipe.get('name'),
                        image: image.get('tag'),
                        cookbook: self.cookbookscol.get(recipe.get('cookbook')).get('name'),
                        system: image.get('system')
                    });
                    self.deploymentscol.add(d);
                });
            });
            this.deploymentsview.render();
        },

        run_deployments: function () {
            this.deploymentscol.each(function(d){
               console.log("Launching" + d.get('recipe'));
                d.save_remote(this.get_credentials());
            }, this);
        }
    });
});