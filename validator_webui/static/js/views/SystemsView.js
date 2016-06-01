/**
 * Created by Administrator on 18/05/2016.
 */
define(function (require) {
    "use strict";

    var Backbone = require('backbone'),
        SystemView = require('views/SystemView');

    return Backbone.View.extend({
        el: "#syslist",
        modelView: SystemView,
    });
    
});