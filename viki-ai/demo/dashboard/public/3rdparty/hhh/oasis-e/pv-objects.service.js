(function() {
    'use strict';
    angular
        .module('directives.kinnser.am-print-view.object-service', [])
        .factory('pvObjects', pvObjects);

    pvObjects.$inject = ['pageConstants'];

    
    function pvObjects(pageConstants) {
        var pages = [],
            currentPage = {
                index: 0,
                sections: []
            },
            currentSection = {
                header: "",
                sectionIndex: 0,
                rows: []
            },
            currentPageHeight = 0,
            rowIndex = 0,
            sectionIndex = 0,
            pageIndex = 0;

        return {
            getPages: getPages,

            pushPage: pushPage,

            setSectionHeader: setSectionHeader,
            pushSection: pushSection,

            pushRow: pushRow,
            resetAll: resetAll,
            getConsumedPageHeight: getConsumedPageHeight,
            updateConsumedPageHeight: updateConsumedPageHeight,
            resetConsumedPageHeight: resetConsumedPageHeight,
            getPageRemainingHeight: getPageRemainingHeight
        };

        function getPages() {
            return pages;
        }

        function pushPage() {
            var tempPage = {};

            tempPage.index = pageIndex;
            tempPage.sections = currentPage.sections;

            pages.push(tempPage);

            ++pageIndex;

            recycle("page");

            resetConsumedPageHeight();
        }

        function setSectionHeader(headerName) {
            currentSection.header = angular.isDefined(headerName) ? headerName : "";
        }

        function pushSection() {
            var tempSection = {};

            tempSection.sectionIndex = sectionIndex;
            tempSection.header = currentSection.header;
            tempSection.row = currentSection.rows;

            (currentPage.sections).push(tempSection);

            ++sectionIndex;

            recycle("section");
        }

        function pushRow(row) {
            var tempRow = {};

            tempRow = row;
            tempRow.rowIndex = rowIndex;
            (currentSection.rows).push(tempRow);
            ++rowIndex;
        }

        function recycle(target) {
            if (target === "page") {
                currentPage.index = pageIndex;
                currentPage.sections = [];
            } else if (target === "section") {
                currentSection.sectionIndex = sectionIndex;
                currentSection.header = "";
                currentSection.rows = [];
            }
        }

        //page height
        function getConsumedPageHeight() {
            return currentPageHeight;
        }

        function updateConsumedPageHeight(newRowHeight) {
            currentPageHeight = currentPageHeight + newRowHeight;
        }

        function resetConsumedPageHeight() {
            currentPageHeight = 0;
        }

        function getPageRemainingHeight() {
            if (pageIndex === 0) {
                return (pageConstants.firstPageHeight - currentPageHeight);
            } else {
                return (pageConstants.otherPagesHeight - currentPageHeight);
            }
        }
        function resetAll(){
            pages = [],
            currentPage = {
                index: 0,
                sections: []
            },
            currentSection = {
                header: "",
                sectionIndex: 0,
                rows: []
            },
            currentPageHeight = 0,
            rowIndex = 0,
            sectionIndex = 0,
            pageIndex = 0;
        }
    }
})();