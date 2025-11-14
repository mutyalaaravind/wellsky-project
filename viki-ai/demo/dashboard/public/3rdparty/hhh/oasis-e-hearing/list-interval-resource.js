angular.module('resources.list-interval', ['resources.RESTResource']).factory('ListInterval', ['RESTResource', function (RESTResource) {

    var ListInterval = RESTResource('ListInterval');

    ListInterval.getListInterval = function(){
    	return ListInterval.query({});
    };


    return ListInterval;

}]);