angular.module('resources.language', ['resources.RESTResource']).factory('Language', ['RESTResource', function (RESTResource) {

    var Language =  RESTResource('Language');

    return Language;

}]);