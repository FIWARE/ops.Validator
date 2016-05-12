/**
 * Created by Administrator on 12/05/2016.
 */
var CookBooks = Backbone.Collection.extend({
    url: '/cookbooks',
    model: CookBook,
});