/**
 * Created by pm.verdugo@dit.upm.es on 12/05/2016.
 */
define(function (require) {
    "use strict";
    var Backbone = require('backbone'),
        config = require('config')
        System = require('models/SystemModel');

    return Backbone.Collection.extend({
        url: config + '/systems',
        model: System,
    });
});
