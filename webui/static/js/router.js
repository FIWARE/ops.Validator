/**
 * Created by Administrator on 18/05/2016.
 */
define(function (require) {
    "use strict";
    var Backbone = require('backbone'),
        CookBooksView = require('views/CookBooksView');

    return Backbone.Router.extend({

        routes: {
            "": "home",

        },

        home: function () {
        },
    })
});
