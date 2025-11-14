(function() {
    'use strict';
    angular
        .module('directives.kinnser.am-print-view.oneCellType2', [])
        .factory('oneCellType2', oneCellType2);

    oneCellType2.$inject = ['pageConstants', 'pvObjects', 'lineInterpreterService'];

    function oneCellType2(pageConstants, pvObjects, lineInterpreterService) {
        return {
            execute: execute
        };

        function execute(row) {
            var symmetricArray = [],
                padding = pageConstants.rowPaddingTop + pageConstants.rowPaddingBottom,
                tempRow = {
                    columns: [{
                        cells: [{
                            index: 1,
                            title: "",
                            body: "",
                            childCells: [],
                            titleList: []
                        }]
                    }]
                },
                remainingPageHeight = pvObjects.getPageRemainingHeight() - padding - pageConstants.lineHeight,
                lineCapacity = Math.floor(remainingPageHeight / pageConstants.lineHeight),
                lastBreakIndex = 0,
                firstBreakIndex = 0,
                pageMaxBreakIndex = 0,
                titleFlag = false;

            symmetricArray = getSymmetricArray(row);

            if (pvObjects.getPageRemainingHeight() < pageConstants.unitRowHeight) {
                pvObjects.pushSection();
                pvObjects.pushPage();
            }

            if (symmetricArray.length < lineCapacity) {
                tempRow.rowHeader = row.rowHeader;
                tempRow.columns[0].cells[0].titleList = row.columns[0].cells[0].titleList;
                tempRow.columns[0].cells[0].cellLayout = row.columns[0].cells[0].cellLayout;
                tempRow.columns[0].cells[0].childCells = symmetricArray;
                tempRow.layout = row.layout;
                tempRow.rowHeight = (symmetricArray.length * pageConstants.lineHeight) + pageConstants.lineHeight + padding;
                pvObjects.updateConsumedPageHeight(tempRow.rowHeight);
                pvObjects.pushRow(tempRow);
            } else {
                do {
                    remainingPageHeight = pvObjects.getPageRemainingHeight() - padding - pageConstants.lineHeight;
                    var subArray = [],
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
                        lastBreakIndex = firstBreakIndex + pageMaxBreakIndex < symmetricArray.length ? pageMaxBreakIndex : symmetricArray.length;
                        subArray = symmetricArray.slice(firstBreakIndex, firstBreakIndex + lastBreakIndex);

                        firstBreakIndex = firstBreakIndex + lastBreakIndex;

                        tempRow.rowHeader = row.rowHeader;
                        tempRow.columns[0].cells[0].titleList = row.columns[0].cells[0].titleList;
                        tempRow.columns[0].cells[0].cellLayout = row.columns[0].cells[0].cellLayout;
                        tempRow.columns[0].cells[0].childCells = subArray;
                        tempRow.layout = row.layout;
                        tempRow.rowHeight = (subArray.length * pageConstants.lineHeight) + pageConstants.lineHeight + padding;

                        if (titleFlag) {
                            tempRow.rowHeader = "(Continued) " + row.rowHeader;
                            tempRow.rowTopMargin = false;
                            pvObjects.updateConsumedPageHeight(pageConstants.rowHeaderHeight);
                        } else {
                            tempRow.rowHeader = row.rowHeader;
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
                } while (firstBreakIndex < symmetricArray.length);
            }
        }

        function getSymmetricArray(row) {
            var properties = Object.keys(row.columns[0].cells[0].titleList[0]),
                childCells = row.columns[0].cells[0].childCells,
                layout = row.columns[0].cells[0].cellLayout,
                absoluteData = [],
                tempCells = [],
                maxLength = 0,
                charSpan2 = 15,
                charSpan6 = 49,
                charSpan8 = 62,
                charSwitch = 0;
            for (var childCell = 0; childCell < childCells.length; childCell++) {
                for (var property in childCells[childCell]) {
                    var charSize = [],
                        tempMonoLines = [];
                    if (layout === "threeColumn-t1") {
                        charSize = [charSpan2, charSpan8, charSpan2];
                        tempMonoLines = [];
                        tempMonoLines = lineInterpreterService.getMonoLines(childCells[childCell][property], charSize[charSwitch]);
                        if (tempMonoLines.length > maxLength) {
                            maxLength = tempMonoLines.length;
                        }
                        tempCells.push(tempMonoLines);
                    } else if (layout === "twoColumn-t1") {
                        charSize = [charSpan6, charSpan6];
                        tempMonoLines = [];
                        tempMonoLines = lineInterpreterService.getMonoLines(childCells[childCell][property], charSize[charSwitch]);
                        if (tempMonoLines.length > maxLength) {
                            maxLength = tempMonoLines.length;
                        }
                        tempCells.push(tempMonoLines);
                    }
                    charSwitch++;
                }
                charSwitch = 0;

                for (var monoLine = 0; monoLine < maxLength; monoLine++) {
                    var finalObjectToPush = {},
                        prop = 0;
                    for (prop = 0; prop < properties.length; prop++) {
                        finalObjectToPush[properties[prop]] = angular.isDefined(tempCells[prop][monoLine]) ? tempCells[prop][monoLine] : "";
                    }
                    absoluteData.push(finalObjectToPush);
                }
                tempCells = [];
                maxLength = 0;
            }
            return absoluteData;
        }
    }
})();