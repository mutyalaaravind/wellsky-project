(function() {
    'use strict';
    angular
        .module('directives.kinnser.am-print-view.page', [])
        .directive('kPage', kPage);

    kPage.$inject = ['Envi'];

    function kPage(Envi) {
        return {
            templateUrl: Envi.envi + "directives/page/page.tpl.html",
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
