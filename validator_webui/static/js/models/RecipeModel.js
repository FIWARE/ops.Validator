/**
 * Created by pm.verdugo@dit.upm.es on 12/05/2016.
 */
define(function (require) {
    "use strict";
    var Backbone = require('backbone'),
        bbsel = require('bbselect');
    return Backbone.Model.extend({
        initialize: function () {
            // Applies the mixin:
            Backbone.Select.Me.applyTo(this);
        }
    });
});
