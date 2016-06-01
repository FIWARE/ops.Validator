/**
 * Created by pm.verdugo@dit.upm.es on 12/05/2016.
 */
define(function (require) {
    "use strict";
    var Backbone = require('backbone'),
        config = require('config')
        Recipe = require('models/RecipeModel'),
        Recipes = Backbone.Collection.extend({
            url: config + '/recipes',
            model: Recipe,
        });
    return Recipes;
});
