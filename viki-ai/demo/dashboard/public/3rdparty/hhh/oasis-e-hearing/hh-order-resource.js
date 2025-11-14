angular.module('resources.hh-order-resource', ['resources.RESTResource']).factory('HHOrder', ['RESTResource', function (RESTResource) {
    var HHOrder = RESTResource('HHOrder');

    // Post Hospital Order
    HHOrder.buildPHO = function(phoData){
        return HHOrder.insert({
            path: 'PostHospitalOrder/Build',
            data: phoData
        });
    };
    
    HHOrder.updatePHO = function(phoData){
        return HHOrder.update({
            path: 'PostHospitalOrder/Update',
            data: phoData
        });
    };
    
    HHOrder.updatePHONarratives = function(phoData){
        return HHOrder.update({
            path: 'PostHospitalOrder/UpdateNarratives',
            data: phoData
        });
    };
    
    HHOrder.byPatientTask = function(clinicBranchKey, patientKey, patientTaskKey){
        return HHOrder.query({
            path: 'PostHospitalOrder/clinicBranch/'+clinicBranchKey+'/patient/'+patientKey+'/patientTask/'+patientTaskKey
        });
    };
    
    
    HHOrder.getPHOPrintViewData = function(patientKey,patientTaskKey){
        return HHOrder.query({
            path: 'PostHospitalOrderPrintView/patient/'+patientKey+'/patientTask/'+patientTaskKey            
        });
    };
    
    // SCIC Order
    HHOrder.buildSCICO = function(scicoData){
        return HHOrder.insert({
            path: 'SCICOrder/Build',
            data: scicoData
        });
    };
    
    HHOrder.getSCICObyPatientTask = function(clinicBranchKey, patientKey, patientTaskKey){
        return HHOrder.query({
            path: 'SCICOrder/clinicBranch/'+clinicBranchKey+'/patient/'+patientKey+'/patientTask/'+patientTaskKey
        });
    };
    
    HHOrder.updateSCICO = function(scicoData){
        return HHOrder.update({
            path: 'SCICOrder/Update',
            data: scicoData
        });
    };
    
    HHOrder.updateSCICONarratives = function(scicoData){
        return HHOrder.update({
            path: 'SCICOrder/UpdateNarratives',
            data: scicoData
        });
    };
    
    HHOrder.getChangeOfCareTypes = function(patientKey, patientTaskKey){
        return HHOrder.query({
            path: 'changeOfCareTypes'
        });
    };
    
    HHOrder.submitOrder = function(orderData){
        return HHOrder.update({
            path: 'Submit',
            data: orderData
        });
    };
    
    HHOrder.returnOrder = function(orderData){
        return HHOrder.update({
            path: 'Return',
            data: orderData
        });
    };

    HHOrder.approveOrder = function(orderData){
        return HHOrder.update({
            path: 'Approve',
            data: orderData
        });
    };

    return HHOrder;
}]);
