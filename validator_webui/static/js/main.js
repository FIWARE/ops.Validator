/**
 * Created by Administrator on 18/05/2016.
 */
require.config({
    baseUrl: './js',
    paths: {
        jquery: 'lib/jquery-2.2.3',
        underscore: 'lib/underscore',
        backbone: 'lib/backbone',
        config: 'config'
    }

});

require(['app',], function(App){
    App.initialize();
});

