(function() {
    'use strict';
    angular
        .module('directives.kinnser.am-print-view.page-section', [])
        .directive('kPageSection', kPageSection);

    kPageSection.$inject = ['Envi'];

    function kPageSection(Envi) {
        return {
            templateUrl: Envi.envi + "/directives/page-section/page-section.tpl.html",
            restrict: "EA",
            replace: true,
            scope: {
                section: "=sectionModel",
                idSuffix: '@',
                pageNo: '@',
                showSectionHeader: '='
            }
        };
    }
})();