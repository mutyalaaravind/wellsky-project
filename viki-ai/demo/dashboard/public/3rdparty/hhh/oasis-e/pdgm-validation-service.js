(function() {
    'use strict';

    var pdgmValidationService = angular.module('services.pdgm.pdgm-validation', [])
    pdgmValidationService.factory('PdgmValidationService', ['$http', function($http){
        var PdgmValidationService = {};

        PdgmValidationService.validateICD10Code = function(clinicKey, episodeKey, ICDCode, taskTargetDate ){
            
            return $http.get('/rest/V1/PDGMValidation/Clinic/'+clinicKey+'/Episode/'+episodeKey+'/ICD10/'+ICDCode +'?TaskTargetDate='+ taskTargetDate);
        }

        PdgmValidationService.validateICD10CodeClinicOnly = function (clinicKey, ICDCode, taskTargetDate) {
            return $http.get('/rest/V1/PDGMValidation/Clinic/' + clinicKey + '/ICD10/' + ICDCode + '?TaskTargetDate=' + taskTargetDate);
        }

        return PdgmValidationService
    }] )

}) ();
