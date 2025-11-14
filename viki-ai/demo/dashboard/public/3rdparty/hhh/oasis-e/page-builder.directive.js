(function() {
    'use strict';
    angular
        .module('directives.kinnser.am-print-view.page-builder', [
            'directives.kinnser.am-print-view.page.constants',
            'directives.kinnser.am-print-view.oneCellType1',
            'directives.kinnser.am-print-view.oneCellType2',
            'directives.kinnser.am-print-view.object-service',
            'directives.kinnser.am-print-view.page-builder-service',
            'directives.kinnser.am-print-view.layout-mapper-service',
            'directives.kinnser.am-print-view.line-interpreter-service',
            'directives.kinnser.am-print-view.page',
            'directives.kinnser.am-print-view.page-section',
            'directives.kinnser.am-print-view.row-builder',
            'directives.kinnser.am-print-view.cell'
        ])
        //  Dev: /AM/EHR/amng/am-print-view/

    .constant('Envi', {
            envi: '/EHR/amng/am-print-view/'
        })
        .directive('kPageBuilder', kPageBuilder);

    kPageBuilder.$inject = ['Envi'];

    function kPageBuilder(Envi) {
        return {
            templateUrl: Envi.envi + "directives/page-builder/page-builder.tpl.html",
            restrict: "EA",
            controller: ['$scope', 'pageBuilderService', PageBuilderContoller],
            scope: {
                data: "=printModel",
                idSuffix: '@?',
                isPrintView: '=?',
                orderNumber: '@',
                pageHeader: "="
            }
        };
    }

    function PageBuilderContoller($scope, pageBuilderService) {

        // handles suffix for id's at each element
        $scope.idSuffix = angular.isDefined($scope.idSuffix) ? $scope.idSuffix : "Print_View"

        // enable and disable page header and page breaks for print view
        $scope.isPrintView = angular.isDefined($scope.isPrintView) ? $scope.isPrintView : true;

        if ($scope.isPrintView) {
            $scope.pages = pageBuilderService.getPages($scope.data);
        } else {
            $scope.pages = ([{
                index: 0,
                sections: $scope.data
            }]);
        }
    }
})();
