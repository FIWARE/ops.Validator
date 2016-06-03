/**
 * Created by pm.verdugo@dit.upm.es on 12/05/2016.
 */
define(function (require) {

    "use strict";

    var Backbone = require('backbone'),
        config = require('config'),
        Deployment = require('models/DeploymentModel'),
        basicauth = require('bbbasicauth');

    return Backbone.Collection.extend({
        url: config.api_url + '/deployments/',
        model: Deployment,

    });
});
