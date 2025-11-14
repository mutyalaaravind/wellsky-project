angular.module('resources.infection-patient', ['resources.RESTResource'])
    .factory('InfectionPatient', ['RESTResource', 'DarkDeployService', function (RESTResource, DarkDeployService) {

    var InfectionPatient = RESTResource('InfectionPatient');

    if (DarkDeployService.isApplicationFeatureEnabled('DARK_DEPLOY_HCL-12403_Use_QualityControl_GCP')) {
        InfectionPatient.baseUrl = '/wsh/operations/quality-control/api';
    } else {
        InfectionPatient.baseUrl = '/operations/quality-control/api';
    }
    InfectionPatient.apiVersion = 'v1';

    InfectionPatient.getSecondPartBaseUrl = function(clinicKey, clinicBranchKey, apiVersion) {
        return apiVersion + '/Clinic/' + clinicKey + '/ClinicBranch/' + clinicBranchKey  + '/';
    };

    InfectionPatient.getPatientsBaseUrl = function(clinicKey, patientKey, apiVersion) {
        return apiVersion + '/Clinic/' + clinicKey + '/Patients/' + patientKey  + '/';
    };

    var isIE = function() {
        ua = navigator.userAgent;
        var is_ie = ua.indexOf("MSIE ") > -1 || ua.indexOf("Trident/") > -1;
        return is_ie;
    };

    InfectionPatient.headers = isIE() ?
    {
        'If-Modified-Since': 'Sat, 26 Jul 1997 05:00:00 GMT',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache'
    }:{
            'Cache-Control': 'no-cache'
    };

    InfectionPatient.insertInfectionPatient = function(clinicKey, clinicBranchKey, patientInformation) {
        return InfectionPatient.insertWithHeaders({
            path: InfectionPatient.getSecondPartBaseUrl(clinicKey, clinicBranchKey, InfectionPatient.apiVersion)+'InfectionLogs',
            url: InfectionPatient.baseUrl,
            data: angular.toJson(patientInformation),
            headers: {
                'Content-Type': 'application/json'
            },
            successCallback: function(response, status) {
                response.status = status;
            }
        });
    };

    InfectionPatient.updateInfectionPatient = function(clinicKey, clinicBranchKey, infectionKey, patientInformation) {
        return InfectionPatient.updateWithPutJson({
            path: InfectionPatient.getSecondPartBaseUrl(clinicKey, clinicBranchKey, InfectionPatient.apiVersion)+'InfectionLogs/'+infectionKey,
            url: InfectionPatient.baseUrl,
            data: angular.toJson(patientInformation),
            headers: {
                'Content-Type': 'application/json'
            },
            successCallback: function(response, status) {
                response.status = status;
            }
        });
    };

    InfectionPatient.closeInfectionPatient = function(clinicKey, clinicBranchKey, infectionKey, patientInformation) {
        return InfectionPatient.updateWithPutJson({
            path: InfectionPatient.getSecondPartBaseUrl(clinicKey, clinicBranchKey, InfectionPatient.apiVersion)+'InfectionLogs/Close/' + infectionKey,
            url: InfectionPatient.baseUrl,
            data: angular.toJson(patientInformation),
            headers: {
                'Content-Type': 'application/json'
            },
            successCallback: function(response, status) {
                response.status = status;
            }
        });
    };

    InfectionPatient.getInfectionPatientInformation = function(clinicKey, clinicBranchKey, infectionKey){
            return InfectionPatient.query({
                path: InfectionPatient.getSecondPartBaseUrl(clinicKey, clinicBranchKey, InfectionPatient.apiVersion)+'InfectionLogs/'+infectionKey,
                url: InfectionPatient.baseUrl,
                headers: InfectionPatient.headers
        });
    };

    InfectionPatient.getInfectionLogsByPatient = function(clinicKey, patientKey){
        return InfectionPatient.query({
            path: InfectionPatient.getPatientsBaseUrl(clinicKey, patientKey, InfectionPatient.apiVersion)
            + 'Infections',
            url: InfectionPatient.baseUrl,
            headers: InfectionPatient.headers
        });
    };

    InfectionPatient.deleteInfectionPatientInformation = function(clinicKey, clinicBranchKey, infectionKey){
        return InfectionPatient.delete({
            path: InfectionPatient.getSecondPartBaseUrl(clinicKey, clinicBranchKey, InfectionPatient.apiVersion)+'InfectionLogs/'+infectionKey,
            url: InfectionPatient.baseUrl
        });
    };

    InfectionPatient.getInfectionLogPdfInformation = function(clinicKey, clinicBranchKey, infectionKey) {
        return InfectionPatient.query({
            path: InfectionPatient.getSecondPartBaseUrl(clinicKey, clinicBranchKey, InfectionPatient.apiVersion)
                + 'InfectionLogs/Print/' + infectionKey,
            url: InfectionPatient.baseUrl,
            headers: InfectionPatient.headers
        });
    }

    return InfectionPatient;
}]);
