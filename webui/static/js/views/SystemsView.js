/**
 * Created by Administrator on 18/05/2016.
 */
define(function (require) {
    "use strict";

    var CollectionView = require('collectionview'),
        SystemView = require('views/SystemView');
    
    return CollectionView.extend({
        el: "#syslist",
        modelView: SystemView,
        selectable : true,
        selectMultiple : true,
    });
    
});