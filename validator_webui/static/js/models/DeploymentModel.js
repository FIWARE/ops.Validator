/**
 * Created by pm.verdugo@dit.upm.es on 12/05/2016.
 */
define(function (require) {
    "use strict";
    var Backbone = require('backbone');
    return Backbone.Model.extend({
        save_remote: function (credentials) {
            this.id = null;
            this.credentials = credentials;
            this.name = "test";
            this.save();
        }
    });
});