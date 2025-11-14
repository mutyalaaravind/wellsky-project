angular.module('resources.list-frequency', ['resources.RESTResource']).factory('ListFrequency', ['RESTResource', function (RESTResource) {

    var ListFrequency = RESTResource('ListFrequency');

    ListFrequency.getListFrequency = function(){
    	return ListFrequency.query({});
    };

    return ListFrequency;

}]);