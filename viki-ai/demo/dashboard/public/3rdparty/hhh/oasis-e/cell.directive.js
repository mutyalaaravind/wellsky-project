(function() {
    'use strict';
    angular
        .module('directives.kinnser.am-print-view.cell', [])
        .directive('kCell', kCell);

    kCell.$inject = ['Envi', 'lineInterpreterService'];

    function kCell(Envi, lineInterpreterService) {
        return {
            templateUrl: Envi.envi + "directives/cell/cell.tpl.html",
            restrict: "EA",
            replace: true,
            link: printViewCell,
            scope: {
                cell: "=cellModel",
                cellHeight: "@"
            }
        };

        function printViewCell(scope, element, attrs) {

            var incomingLineLength,
                isFullLine,
                lineCount,
                resultLineLength,
                tallestCell;
            element.css({
                "height": (scope.cellHeight) + "px"
            });
            scope.getPropertyName = function() {
                return Object.keys(scope.cell.titleList[0]);
            };
            // Math.ceil to set the maximum line height for a cell based on objects length
            function calculateDynamicCellHeight(cellValue, tallestCell, availableLineLength) {
                var totalLines = lineInterpreterService.getMonoLines(cellValue[scope.getPropertyName()[tallestCell]], availableLineLength);
                return '' + totalLines.length * 14 + 'px';
            }

            function calculateDefaultAndLastCellHeight(lastCellIndex) {
                return !lastCellIndex ? '14px' : '19px';
            }
            scope.getCellHeight = function(cellValue, indexValue, lastCellIndex, compareWithIndex) {
                if (compareWithIndex) {
                	if (cellValue[scope.getPropertyName()[compareWithIndex]]) {
	                    return cellValue[scope.getPropertyName()[compareWithIndex]].length > 80 ? calculateDynamicCellHeight(cellValue, compareWithIndex, 80) : calculateDefaultAndLastCellHeight(lastCellIndex);
                	}
                	else {
                		calculateDefaultAndLastCellHeight(lastCellIndex);
                	}
                	
                } else {
                    // To get the object property which has more characters
                    tallestCell = cellValue[scope.getPropertyName()[1]].length > cellValue[scope.getPropertyName()[0]].length ? 1 : 0;
                    // To calculate the height based on the tallestCell value
                    return cellValue[scope.getPropertyName()[tallestCell]].length > 60 ? calculateDynamicCellHeight(cellValue, tallestCell, 60) : calculateDefaultAndLastCellHeight(lastCellIndex);
                }
            };

            if (angular.isDefined(scope.cell.body) && scope.cell.body.length && ((scope.cell.body).indexOf('\\n') > -1)) {
                scope.cell.body = scope.cell.body.replace(/\\n/ig, "<br />");
            } else if (angular.isDefined(scope.cell.body) && scope.cell.body.length && scope.cell.body.split('\n').length) {
                scope.cell.body = scope.cell.body.replace(new RegExp('\n', 'g'), "<br />");
            }
        }
    }
})();