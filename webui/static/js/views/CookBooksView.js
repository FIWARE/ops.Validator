/**
 * Created by Administrator on 18/05/2016.
 */
define(function (require) {
    "use strict";

    var Backbone = require('backbone'),
        CookBookView = require('views/CookBookView'),
        CookBooks = require('models/CookBooksModel');

    return Backbone.View.extend({
        model: CookBooks,
        tagname: 'select',
        id: 'cblist',

        render: function () {
            this.$el.html(); // lets render this view

            for (var i = 0; i < this.model.length; ++i) {
                // lets create a book view to render
                var m_cookbookView = new CookBookView({model: this.model.at(i)});

                // lets add this book view to this list view
                this.$el.append(m_cookbookView.$el);
                m_cookbookView.render(); // lets render the book           
            }

            return this;
        },
    });

});