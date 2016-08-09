/**
 * Created by Administrator on 09/08/2016.
 */
define(function (require) {
    "use strict";

    var Backbone = require('backbone'),
        _ = require("underscore");

    var NotificationView = Backbone.View.extend({

        targetElement: '#message',

        tagName: 'div',

        className: 'notification',

        defaultMessages: {
            'success': 'Success!',
            'error': 'Sorry! An error occurred in the process',
            'warning': 'Are you sure you want to take this action?',
            'info': 'An unknown event occurred'
        },

        cssClasses: {
            'success': 'success',
            'error': 'error',
            'warning': 'warning',
            'info': 'info'
        },

        events: {
            "click": "closeNotification",
        },

        automaticClose: false,

        initialize: function () {
            // defaults
            var type = 'info';
            var text = this.defaultMessages[type];
            var target = this.targetElement;
        },

        render: function (options) {
            // defaults
            var type = 'info';
            var text = this.defaultMessages[type];
            var target = this.targetElement;
            // if any options were set, override defaults
            if (options && options.hasOwnProperty('type'))
                type = options.type;
            if (options && options.hasOwnProperty('text'))
                text = options.text;
            if (options && options.hasOwnProperty('target'))
                target = options.target;
            if (options && options.hasOwnProperty('automaticClose'))
                this.automaticClose = options.automaticClose;
            this.$el.removeClass();
            this.$el.addClass(this.cssClasses[type]);
            this.$el.text(text);
            this.$el.prependTo(this.targetElement);

            // Automatically close after set time. also closes on click
            var self = this;
            if (this.automaticClose) {
                setTimeout(function () {
                    self.closeNotification();
                }, 3000);
            }
        },

        closeNotification: function () {

            var self = this;

            $(this.el).fadeOut(function () {
                self.unbind();
                self.remove();
            });
        }

    });
    var instance;

    return function() {
        if (!instance) {
            instance = new NotificationView();
        }
        return instance;
    }
});
