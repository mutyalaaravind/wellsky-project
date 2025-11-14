(function() {
    'use strict';
    angular
        .module('directives.kinnser.am-print-view.oneCellType1', [])
        .factory('oneCellType1', oneCellType1);

        oneCellType1.$inject = ['pageConstants', 'pvObjects', 'lineInterpreterService'];

    function oneCellType1(pageConstants, pvObjects, lineInterpreterService) {
        return {
            execute: execute
        };

        function execute(row) {

            var cellBody = row.columns[0].cells[0].body,
                cellTitle = row.columns[0].cells[0].title,
                totalLines = [],
                lastBreakIndex = 0,
                firstBreakIndex = 0,
                pageMaxBreakIndex = 0,
                padding = pageConstants.rowPaddingTop + pageConstants.rowPaddingBottom,
                titleFlag = false;

            totalLines = lineInterpreterService.getMonoLines(cellBody, pageConstants.charSpan12);

            if (pvObjects.getPageRemainingHeight() < pageConstants.unitRowHeight) {
                pvObjects.pushSection();                
                pvObjects.pushPage();
            }

            if (pvObjects.getPageRemainingHeight() > ((totalLines.length * pageConstants.lineHeight) + pageConstants.lineHeight + padding)) {
                // row height = body height + title height + top padding + bottom padding
                row.rowHeight = (totalLines.length * pageConstants.lineHeight) + pageConstants.lineHeight + padding;
                row.columns[0].cells[0].body = totalLines.join('');
                pvObjects.pushRow(row);
                pvObjects.updateConsumedPageHeight(row.rowHeight);
            } else {

                do {
                    var remainingPageHeight = pvObjects.getPageRemainingHeight() - padding - pageConstants.lineHeight,
                        subArray = [],
                        tempRow = {
                            columns: [{
                                cells: [{
                                    index: 1,
                                    title: "",
                                    body: ""
                                }]
                            }]
                        };
                    if (remainingPageHeight > pageConstants.unitRowHeight) {
                        pageMaxBreakIndex = Math.floor(remainingPageHeight / pageConstants.lineHeight);
                        lastBreakIndex = firstBreakIndex + pageMaxBreakIndex < totalLines.length ? pageMaxBreakIndex : totalLines.length;
                        subArray = totalLines.slice(firstBreakIndex, firstBreakIndex + lastBreakIndex);

                        firstBreakIndex = firstBreakIndex + lastBreakIndex;

                        tempRow.columns[0].cells[0].body = subArray.join('');
                        tempRow.rowTopMargin = row.rowTopMargin;
                        tempRow.layout = row.layout;
                        tempRow.rowHeight = (subArray.length * pageConstants.lineHeight) + pageConstants.lineHeight + padding;
                        tempRow.rowHeader= (row.rowHeader!=='undefined'|| row.rowHeader!=="")?row.rowHeader:"";
                        if (titleFlag) {
                            tempRow.columns[0].cells[0].title = "(Continued) " + ((cellTitle!= undefined)?cellTitle: ((row.rowHeader!==undefined)?row.rowHeader:""));
                            tempRow.rowTopMargin = false;
                        } else {
                            tempRow.columns[0].cells[0].title = cellTitle;
                            tempRow.rowTopMargin = row.rowTopMargin;
                        }

                        titleFlag = true;

                        pvObjects.updateConsumedPageHeight(tempRow.rowHeight);                
                        pvObjects.pushRow(tempRow);
                        if (pvObjects.getPageRemainingHeight() < pageConstants.unitRowHeight) {
                            pvObjects.pushSection();
                            pvObjects.pushPage();
                        }
                    } else {
                        pvObjects.pushSection();                        
                        pvObjects.pushPage();
                    }
                } while(firstBreakIndex < totalLines.length);   
            }            
        }
    }
})();