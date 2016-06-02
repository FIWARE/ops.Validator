/**
 * Created by Administrator on 02/06/2016.
 */
define(function (require) {
    "use strict";

    var Backbone = require('backbone'),
        RecipesView = require("views/RecipesView"),
        ImagesView = require("views/ImagesView"),
        RecipeCollection = require("models/RecipeCollection"),
        CookbookCollection = require("models/CookbookCollection"),
        CookbooksView = require("views/CookbooksView"),
        ImageCollection = require("models/ImageCollection");

    return Backbone.View.extend({

        el: $("#validator_app"),

        events: {
            "click #button_refresh"   : "refreshRecipes",
            "click #button_add"   : "add_to_deployments",
            "click #button_run"   : "run_deployments",
        },

        initialize: function () {
            console.log("Booting...")
            this.username = this.$("#username");
            this.password = this.$("#password");
            this.render();
        },

        render: function () {
            this.imagescol = new ImageCollection(this.get_credentials());
            var imagessel = new ImagesView({collection: this.imagescol});
            this.cookbookscol = new CookbookCollection(this.get_credentials());
            var cookbookssel = new CookbooksView({collection: this.cookbookscol});
            this.recipescol = new RecipeCollection(this.get_credentials());
            var recipessel = new RecipesView({collection: this.recipescol});
        },

        get_credentials: function(){
            return {
                    username: this.username.val(),
                    password: this.password.val()
                }
        },

        refreshRecipes: function(){
            var creds = this.get_credentials();
            new CookbookCollection().refresh(creds);
            var recipesCollection = new RecipeCollection(creds);
            var recipesRows = new RecipesView({collection: recipesCollection});
        },

        add_to_deployments: function () {
            console.log(this.imagescol.selected);
            console.log(this.cookbookscol.selected);
            console.log(this.recipescol.selected);
        },

        run_deployments: function () {

        }
    });
});