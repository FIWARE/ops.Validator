/**
 * Created by Administrator on 18/05/2016.
 */
define(function (require) {
    "use strict";
    var CookBook = require('models/CookBookModel'),
        CookBooks = require('models/CookBooksModel'),
        System = require('models/SystemModel'),
        Systems = require('models/SystemsModel'),
        cb1 = new CookBook({id: 1, name: "CookBook 1"}),
        cb2 = new CookBook({id: 2, name: "CookBook 2"}),
        cbCol = new CookBooks([cb1, cb2]),
        sys1 = new System({id: "ubuntu_precise", name:"Ubuntu 12.04"}),
        sys2 = new System({id: "ubuntu_trusty", name:"Ubuntu 14.04"}),
        sys3= new System({id: "centos6", name:"CentOs6"}),
        sys4 = new System({id: "centos7", name:"CentOs7"}),
        sysCol = new Systems([sys1, sys2, sys3, sys4]);
    return {cbCol:cbCol, sysCol:sysCol};
});