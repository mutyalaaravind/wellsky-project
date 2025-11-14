angular.module('resources.icd', ['resources.RESTResource']).factory('ICD', ['RESTResource', function (RESTResource) {

    var ICD = RESTResource('ICD');

    ICD.getDiagnosisCodes = function(filters){
    	return ICD.query({
            path: 'diagnosis/' + sanitize(filters.q),
            params: {
                version: filters.version,
                showSpecific: filters.showSpecific,
                index: filters.index,
                interval: filters.interval,
                targetDate: filters.targetDate
            },
            isArray: true
        });
    };

    ICD.getDiagnosisCodeByCode = function(filters){
    	return ICD.query({
            path: 'diagnosiscode/' + sanitize(filters.q),
            params: {
                showSpecific: filters.showSpecific,
                index: filters.index,
                interval: filters.interval,
                targetDate: filters.targetDate
            },
            isArray: true
        });
    };

    ICD.getProcedureCodes = function(filters){
        return ICD.query({
            path: 'procedure/' + sanitize(filters.q),
            params: {
                version: filters.version,
                index: filters.index,
                interval: filters.interval
            },
            isArray: true
        });
    };

    ICD.getFavoritesList = function(filters){
        return ICD.query({
            path: 'diagnosis/favorites/user/' + filters.userKey,
            params: {
                version: filters.version,
                targetDate: filters.targetDate
            },
            isArray: true
        });
    };

    ICD.addFavoriteDiagnosisCode = function(filters){
         return ICD.insert({
            path: 'diagnosis/favorites/user/'+filters.userKey,
            data: {
                diagnosisCode: filters.diagnosisCode,
                listVersionKey: 2,
                active: 1,
                diagnosisFavoritesKey: 0
            }
        });
    }

    ICD.removeFavoriteDiagnosisCode = function(filters){
        return ICD.insert({
            path: 'diagnosis/favorites/user/'+filters.userKey,
            data: {
                diagnosisCode: filters.diagnosisCode,
                listVersionKey: 2,
                active: 0,
                diagnosisFavoritesKey: filters.diagnosisFavoritesKey
            }
        });
    }

    ICD.getICD10ByICD9Code = function(filters){
        return ICD.query({
            path: 'diagnosis/gem/' + filters.diagnosisCode,
            params: {
                version: filters.version
            },
            isArray: true
        });
    }

    function sanitize(input) {
        return encodeURIComponent(input.replace(/\\/g, ''));
    }

    return ICD;

}]);

