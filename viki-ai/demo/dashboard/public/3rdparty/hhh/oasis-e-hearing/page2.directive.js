(function() {
    'use strict';
    angular
        .module('directives.kinnser.am-print-view.page-new', [])
        .directive('kPageNew', kPageNew);

        kPageNew.$inject = ['Envi'];

    function kPageNew(Envi) {
        return {
            templateUrl: Envi.envi + "directives/page/page2.tpl.html",
            restrict: "EA",
            replace: true,
            scope: {
                idSuffix: '@',
                orderNumber: '@',
                page: '=pageModel',
                pageHeader: '=',
                showPageHeader: '=',
                totalPages: '@'
            }
        };
    }
})();