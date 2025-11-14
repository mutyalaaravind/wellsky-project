(function() {
    'use strict';
    angular
        .module('directives.kinnser.am-print-view.page-builder-service', [])
        .factory('pageBuilderService', pageBuilderService);

    pageBuilderService.$inject = ['pageConstants', 'pvObjects', 'pvLayoutMapperService', 'lineInterpreterService', 'oneCellType1', 'oneCellType2'];

    function pageBuilderService(pageConstants, pvObjects, pvLayoutMapperService, lineInterpreterService, oneCellType1, oneCellType2) {
        return {
            getPages: getPages
        };

        function getPages(sections) {
            var pages = [],
                tempPage = {},
                tempHeight = 0,
                rowIndex = 0,
                sectionIndex = 0,
                pageIndex = 0,
                characterPerLine = 100,
                lineHeight = 14; // in pixels 

            tempPage = {};
            // setting page index
            tempPage.index = pageIndex;
            // initialize page sections 
            tempPage.sections = [];

            for (var section = 0; section < sections.length; section++) {

                var currentSection = sections[section];

                // closes current page object is remaining height of pages is less than unit height of a row
                if (pvObjects.getPageRemainingHeight() < pageConstants.unitRowHeight) {
                    pvObjects.pushPage();
                }

                if (angular.isDefined(currentSection.header)) {
                    // Setting Section Header
                    pvObjects.setSectionHeader(currentSection.header);
                    // adding section header height
                    pvObjects.updateConsumedPageHeight((currentSection.header).length > 0 ? pageConstants.rowHeaderHeight : 0);
                }

                // iterating throught row objects in sections
                for (var row = 0; row < (currentSection.row).length; row++) {

                    var currentRow = currentSection.row[row];

                    // Handles interrupt 
                    if (currentRow.interrupt === "auto") {
                        var sectionHeight = 0,
                            rowHeight = 0,
                            interruptedRow = {};
                        for (var interruptedRow = 0; interruptedRow < (currentSection.row).length; interruptedRow++) {
                            rowHeight = angular.isDefined(currentSection.row[interruptedRow].rowHeight) ? currentSection.row[interruptedRow].rowHeight : pvLayoutMapperService.getRowHeight(currentSection.row[interruptedRow].layout);
                            sectionHeight = sectionHeight + rowHeight;
                        }

                        if (sectionHeight > pvObjects.getPageRemainingHeight()) {
                            pvObjects.pushSection();
                            pvObjects.pushPage();

                            pvObjects.setSectionHeader("");

                            // adds the height of new extended section section height
                            pvObjects.updateConsumedPageHeight(pvLayoutMapperService.getRowHeight(currentRow.layout));

                            // insert the current row in new extended section
                            pvObjects.pushRow(currentRow);
                            continue;
                        }
                    }

                    // Calculating margins
                    if (currentRow.rowTopMargin) {
                        pvObjects.updateConsumedPageHeight(pageConstants.rowTopMargin);
                    }
                    if (currentRow.rowHeader) {
                        pvObjects.updateConsumedPageHeight(pageConstants.rowHeaderHeight);
                    }

                    if (currentRow.layout === 'oneColumn-oneCell-t1' && currentRow.dynamicHeight === true) {
                        oneCellType1.execute(currentRow);
                    } else if (currentRow.layout === 'oneColumn-oneCell-t2' && sections[section].row[row].dynamicHeight === true) {
                        oneCellType2.execute(currentRow);
                    } else {

                        var currentRowHeight = angular.isDefined(currentRow.rowHeight) ? currentRow.rowHeight : pvLayoutMapperService.getRowHeight(currentRow.layout);

                        if ((pvObjects.getPageRemainingHeight() > currentRowHeight)) {

                            // maintains the current height of section height
                            pvObjects.updateConsumedPageHeight(currentRowHeight);
                            pvObjects.pushRow(currentRow);
                        } else {
                            // complete's the page  object
                            pvObjects.pushSection();
                            pvObjects.pushPage();

                            pvObjects.setSectionHeader("");

                            // adds the height of new extended section section height
                            pvObjects.updateConsumedPageHeight(currentRowHeight);

                            // insert the current row in new extended section
                            pvObjects.pushRow(currentRow);

                        }
                    }
                } // row
                pvObjects.pushSection();
                pvObjects.setSectionHeader("");
            }
            pvObjects.pushPage();
            // sections
            return pvObjects.getPages();
        }

        function getParaHeight(paraLength, characterPerLine, lineHeight) {
            var paraLines = paraLength / characterPerLine;

            return (paraLength > characterPerLine ? (paraLines * lineHeight) : lineHeight);
        }
    }
})();