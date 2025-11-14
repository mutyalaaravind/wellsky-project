angular.module('resources.fallTracker-patient', ['resources.RESTResource'])
    .factory('FallTrackerPatient', ['RESTResource', 'DarkDeployService', function (RESTResource, DarkDeployService) {
    var FallTrackerPatient = RESTResource('FallTrackerPatient');

    if (DarkDeployService.isApplicationFeatureEnabled('DARK_DEPLOY_HCL-12403_Use_QualityControl_GCP')) {
        FallTrackerPatient.baseUrl = '/wsh/operations/quality-control/api';
    } else {
        FallTrackerPatient.baseUrl = '/operations/quality-control/api';
    }
    FallTrackerPatient.apiVersion = 'v1';
    var isIE = function() {
        ua = navigator.userAgent;
        var is_ie = ua.indexOf("MSIE ") > -1 || ua.indexOf("Trident/") > -1;
        return is_ie;
    };
    FallTrackerPatient.headers = isIE() ?
        {
            'If-Modified-Since': 'Sat, 26 Jul 1997 05:00:00 GMT',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }:{

        };
    FallTrackerPatient.getPatientsBaseUrl = function(clinicKey,clinicBranchKey, episodeKey, patientKey,dateFrom, apiVersion) {
        return apiVersion + '/FallLogDashboard/episodeKey/'+ episodeKey + '/patientKey/'+ patientKey+'?clinics='+clinicKey.toString() ;
    };
    FallTrackerPatient.getFallsByPatient = function(clinicKey, clinicBranchKey, episodeKey, patientKey, dateFrom){
        var patientURL=  FallTrackerPatient.getPatientsBaseUrl(clinicKey, clinicBranchKey,episodeKey, patientKey, dateFrom,  FallTrackerPatient.apiVersion);
        return FallTrackerPatient.query({
            path: patientURL,
            url: FallTrackerPatient.baseUrl,
            headers: { 'cache-control': 'no-cache' },
            cache: true

        });
    };
    FallTrackerPatient.deleteFall = function(fallLogKey, clinicKey, clinicBranchKey){
        return FallTrackerPatient.delete({
            path: FallTrackerPatient.apiVersion +'/Clinic/'+ clinicKey +'/ClinicBranch/'+clinicBranchKey+'/FallLog/'+ fallLogKey,
            url: FallTrackerPatient.baseUrl
        });
    };

    return FallTrackerPatient;
}]);
