/**
 * Created by Administrator on 12/05/2016.
 */
var CookBookView = Backbone.View.extend({
    model: CookBook,
    tagName: 'li',
    template: '',

    initialize: function() {
        this.template = _.template('<a href="cookbooks/<%= id %>"><%= name %></a>');
    },
    render: function () {
        this.$el.html(this.template(this.model.attributes));
        return this;
    }
});