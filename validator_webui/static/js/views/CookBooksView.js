/**
 * Created by Administrator on 18/05/2016.
 */
define(function (require) {
    "use strict";

    var CollectionView = require('collectionview'),
        CookBookView = require('views/CookBookView'),
        CookBooks = require('models/CookBooksModel');

    return CollectionView.extend({
        el: "#cblist",
        modelView: CookBookView,
        selectable : true,
        selectMultiple : true,
    });
});