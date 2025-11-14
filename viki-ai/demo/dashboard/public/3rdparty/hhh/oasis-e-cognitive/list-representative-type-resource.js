(function(){
    'use strict';
        
    var listRepresentativeType = angular.module('resources.list-representative-type', [
            'resources.RESTResource'
        ]);

    listRepresentativeType.factory('ListRepresentativeType', [
        'RESTResource',
        function( RESTResource ) {
            var listRepresentativeTypeResource = RESTResource('ListRepresentativeType');

            return listRepresentativeTypeResource;
        }
    ]);
})();