/**
 * Created by Administrator on 04/08/2016.
 */

define(function (require) {
    "use strict";
    var _ = require("underscore"),
        Backbone = require('backbone');

    return Backbone.View.extends({

        // some more code here

        events: {
            'submit form': 'uploadFile'
        },

        uploadFile: function (event) {
            var values = {};

            if (event) {
                event.preventDefault();
            }

            _.each(this.$('form').serializeArray(), function (input) {
                values[input.name] = input.value;
            })

            this.model.save(values, {
                iframe: true,
                files: this.$('form :file'),
                data: values
            });
        }
    });
});
