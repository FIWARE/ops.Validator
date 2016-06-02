/**
 * Created by Administrator on 01/06/2016.
 */
/**
 * Created by pm.verdugo@dit.upm.es on 12/05/2016.
 */
define(function (require) {
    "use strict";
    var Backbone = require('backbone')
    //relational = require('relational');
    return Backbone.RelationalModel.extend({
        relations: [{
            type: Backbone.HasMany,
            key: 'recipes',
            relatedModel: 'Recipe',
            collectionType: 'RecipeCollection',
            reverseRelation: {
                key: 'has',
                includeInJSON: 'id'
            }
        }]
    });

});