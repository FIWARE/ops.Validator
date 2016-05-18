/**
 * Created by Administrator on 18/05/2016.
 */
define(function (require) {
    "use strict";
    var Backbone = require('backbone'),
        CookBooksView = require('views/CookBooksView'),
        SystemsView = require('views/SystemsView'),
        dummy = require('models/dummy');

    return Backbone.Router.extend({
        routes: {
            "": "home",
        },

        home: function () {
            var cbookList = new CookBooksView({collection: dummy.cbCol});
            cbookList.render();
            var sysList = new SystemsView({collection: dummy.sysCol})
            sysList.render();
        },
    })
});
