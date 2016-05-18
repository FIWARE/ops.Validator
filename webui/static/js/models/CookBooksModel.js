/**
 * Created by pm.verdugo@dit.upm.es on 12/05/2016.
 */
define(function (require) {
    "use strict";
    var Backbone = require('backbone'),
        CookBook = require('models/CookBookModel'),
        CookBooks = Backbone.Collection.extend({
            url: '/cookbooks',
            model: CookBook,
        });
    return CookBooks;
});
