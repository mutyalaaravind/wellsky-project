angular.module('resources.post-hospital-order-printview', ['resources.RESTResource']).factory('PostHospitalOrderPrintView', ['RESTResource', function (RESTResource) {

    var PostHospitalOrderPrintView =  RESTResource('PostHospitalOrderPrintView');


    PostHospitalOrderPrintView.getPHOPrintViewData = function(patientKey,patientTaskKey){
        return PostHospitalOrderPrintView.query({
            path: 'PostHospitalOrderPrintView/patient/'+patientKey+'/patientTask/'+patientTaskKey            
        });
    };


    return PostHospitalOrderPrintView;

}]);