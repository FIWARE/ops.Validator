/**
 * Created by Administrator on 12/05/2016.
 */
define(function (require) {
    
    var Backbone = require("backbone"),
        Router = require("router");
    
    return {
        initialize: function() {
            var router = new Router();
            Backbone.history.start();
        }
    };
});

