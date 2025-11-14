angular.module('services.util.form-util', []).factory('FormUtilService', [function () {

    var FormUtilService = {};

    /*Converts a result(array of objects) to object to be used in dropdown*/
    FormUtilService.resultToDropdown = function(result, primaryKey, column, castToString, prependBlank, newTextKey, newValKey, prependToColumn, parentKey){
        var dropdownResult = [];
        var obj = {};
        var textKey = newTextKey == undefined ? 'text' : newTextKey;
        var valKey  = newValKey == undefined ? 'value' : newValKey;

        if(angular.isDefined(prependBlank) && prependBlank){
            obj = {};
            obj[textKey] = '';
            obj[valKey] = '';
            dropdownResult.push(obj);
        }
        angular.forEach(result, function(value, key){
            obj = {};
            obj[textKey] = prependToColumn ? result[key][prependToColumn] + ' - ' + result[key][column] : result[key][column];
            obj[valKey] = angular.isDefined(castToString) && castToString  ? String(result[key][primaryKey]) : result[key][primaryKey];
            obj.show = true;
            if(parentKey){
                obj[parentKey] = result[key][parentKey];
                
            }
            dropdownResult.push(obj);
        });
        return dropdownResult;
    };

    return FormUtilService;

}]);