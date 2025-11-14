(function() {
    'use strict';
    angular
        .module('directives.kinnser.am-print-view.line-interpreter-service', [])
        .factory('lineInterpreterService', lineInterpreterService);

    lineInterpreterService.$inject = ['pvLayoutMapperService'];

    function lineInterpreterService(pvLayoutMapperService) {
        return {
            getMonoLines: getMonoLines
        };

        function getMonoLines(para, characterPerLine) {
            var interpretedLines = [];
            interpretedLines = lineInterpreter(para, characterPerLine);
            return (interpretedLines.length > 0 ? interpretedLines : []);
        }

        // TODO: add exception handling for the input parameter
        function lineInterpreter(para, characterPerLine) {
            var paraWithLineBreak = para.split("\n"),
                finalLines = [],
                firstBreakIndex = 0,
                lastBreakIndex = 0,
                tempLine = "",
                delimiters = [',', ';','. ', ' '],
                currentSubPara = "",
                paraTotalHeightInPixel = 0;
            for (var i = 0; i < paraWithLineBreak.length; i++) {
                currentSubPara = paraWithLineBreak[i];

                if (currentSubPara.length <= (characterPerLine)) {
                    finalLines.push(currentSubPara + "\n");
                } else {
                    firstBreakIndex = lastBreakIndex = 0;
                    do {
                        if (currentSubPara[firstBreakIndex + characterPerLine] === " ") {
                            finalLines.push(currentSubPara.substring(firstBreakIndex, firstBreakIndex + characterPerLine) + "\n");
                            firstBreakIndex = firstBreakIndex + characterPerLine + 1;
                        } else if (currentSubPara[firstBreakIndex + characterPerLine] === undefined) {
                            finalLines.push(currentSubPara.substring(firstBreakIndex, currentSubPara.length) + "\n");
                            firstBreakIndex = currentSubPara.length;
                        } else {
                            tempLine = currentSubPara.substring(firstBreakIndex, firstBreakIndex + characterPerLine);

                            lastBreakIndex = -1;
                            for (var delims = 0; delims < delimiters.length; delims++) {
                                var tempIndex = tempLine.lastIndexOf(delimiters[delims]);
                                if (lastBreakIndex < tempIndex) {
                                    lastBreakIndex = tempIndex;
                                }
                            }

                            if (lastBreakIndex === -1) {
                                finalLines.push(currentSubPara.substring(firstBreakIndex, firstBreakIndex + characterPerLine) + "\n");
                                firstBreakIndex = firstBreakIndex + characterPerLine + 1;
                            } else {
                                finalLines.push(currentSubPara.substring(firstBreakIndex, firstBreakIndex + lastBreakIndex) + "\n");
                                firstBreakIndex = firstBreakIndex + lastBreakIndex + 1;
                            }
                        }
                    } while (firstBreakIndex < currentSubPara.length);
                }
            }
            return finalLines;
        }
    }
})();