/**
 * Created by Administrator on 18/05/2016.
 */
define(function (require) {
    "use strict";

    var CollectionView = require('collectionview'),
        RecipeView = require('views/RecipeView'),
        Recipes = require('models/RecipesModel');

    return CollectionView.extend({
        el: "#cblist",
        modelView: RecipeView,
        selectable : true,
        selectMultiple : true,
    });
});