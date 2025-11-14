(function(){
    'use strict';
    
    
    var listRelationshipType = angular.module('resources.list-relationship-type', [
            'resources.RESTResource'
        ]);

    listRelationshipType.factory('ListRelationshipType', [
        'RESTResource',
        function( RESTResource ) {
            var listRelationshipTypeResource = RESTResource('ListRelationshipType');

            return listRelationshipTypeResource;
        }
    ]);
})();