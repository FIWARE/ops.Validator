/**
 * Created by pm.verdugo@dit.upm.es on 12/05/2016.
 */
define(function (require) {
    "use strict";
    var Backbone = require('backbone'),
        System = require('models/SystemModel');

    return Backbone.Collection.extend({
        url: '/systems',
        model: System,
    });
});
