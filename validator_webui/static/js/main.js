/**
 * Created by Administrator on 18/05/2016.
 */
require.config({
    baseUrl: './js',
    paths: {
        jquery: 'lib/jquery-2.2.3',
        underscore: 'lib/underscore',
        backbone: 'lib/backbone',
        // relational: 'lib/backbone-relational',
        bbbasicauth: 'lib/backbone.basicauth',
        bbselect: 'lib/backbone.select',
        config: 'config'
    }
});

define(function (require) {
    "use strict";
    var App = require("app");
    return App.initialize();
});