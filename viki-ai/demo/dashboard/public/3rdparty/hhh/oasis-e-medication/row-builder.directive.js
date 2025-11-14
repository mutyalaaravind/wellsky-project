(function() {
    'use strict';
    angular
        .module('directives.kinnser.am-print-view.row-builder', [])
        .directive('kRowBuilder', kRowBuilder);

    kRowBuilder.$inject = ['Envi'];

    function kRowBuilder(Envi) {
        return {
            templateUrl: Envi.envi + "directives/row-builder/row-builder.tpl.html",
            restrict: "EA",
            replace: true,
            controller: ['$scope', 'pvLayoutMapperService', rowController],
            scope: {
                row: "=rowModel",
                idSuffix: "@",
                pageNo: "@",
                sectionIndex: "@"
            }
        };
    }

    function rowController($scope, pvLayoutMapperService) {

        $scope.getCellHeight = function(layout, columnIndex, cellIndex, rowHeight) {
            return pvLayoutMapperService.getCellHeight(layout, columnIndex, cellIndex, rowHeight);
        };

        $scope.layout = pvLayoutMapperService.getRowLayout($scope.row.layout);

        $scope.getCellStyle = function(value) {
            return value.style;
        };


    }
})();