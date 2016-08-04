/**
 * Created by Administrator on 18/05/2016.
 */
require.config({
    baseUrl: './js',
    paths: {
        jquery: 'lib/jquery-2.2.3',
        jqueryift: 'lib/jquery.iframe-transport',
        underscore: 'lib/underscore',
        backbone: 'lib/backbone',
        bbfileupload: 'lib/backbone.file-upload',
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