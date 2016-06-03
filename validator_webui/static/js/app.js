/**
 * Created by Administrator on 12/05/2016.
 */
define(function (require) {

    var Backbone = require("backbone"),
        AppView = require("views/AppView");

    return {
        initialize: function () {
            //Backbone.emulateJSON = true;
            var appview = new AppView();
            Backbone.history.start();
        }
    };
});

