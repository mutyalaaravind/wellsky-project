(function() {
    'use strict';
    angular
        .module('directives.kinnser.am-print-view.page.constants', [])
        .constant('pageConstants', {
            "firstPageHeight": 910,
            "otherPagesHeight": 880,
            "lineHeight": 14,
            "rowTopMargin": 3,
            "rowPaddingTop": 5,
            "rowPaddingBottom": 5,
            "rowHeaderHeight": 24,
            "unitRowHeight": 38,
            "charSpan12": 100
        });
})();