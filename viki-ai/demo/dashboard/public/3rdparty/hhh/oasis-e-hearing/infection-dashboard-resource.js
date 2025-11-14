angular.module('resources.infection-dashboard',['resources.RESTResource'])
    .factory('InfectionDashboard',
        ['RESTResource', 'DarkDeployService',
            function (RESTResource, DarkDeployService) {

    var InfectionDashboard = RESTResource('InfectionDashboard');

    if (DarkDeployService.isApplicationFeatureEnabled('DARK_DEPLOY_HCL-12403_Use_QualityControl_GCP')) {
      InfectionDashboard.baseUrl = '/wsh/operations/quality-control/api';
    } else {
      InfectionDashboard.baseUrl = '/operations/quality-control/api';
    }
    InfectionDashboard.apiVersion = 'v1';

    var isIE = function() {
        ua = navigator.userAgent;
        var is_ie = ua.indexOf("MSIE ") > -1 || ua.indexOf("Trident/") > -1;
        return is_ie;
    };

    InfectionDashboard.noCacheHeader = isIE() ?
    {
        'If-Modified-Since': 'Sat, 26 Jul 1997 05:00:00 GMT',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache'
    }:{

    };

    InfectionDashboard.getSecondPartBaseUrlWithClinicBranch = function(clinicKey, clinicBranchKey, apiVersion) {
        return apiVersion + '/Clinic/' + clinicKey + '/ClinicBranch/' + clinicBranchKey  + '/InfectionDashboard';
    };


    InfectionDashboard.getSecondPartBaseUrl = function(clinicKey, apiVersion) {
        return apiVersion + '/Clinic/' + clinicKey + '/InfectionDashboard';
    };


    InfectionDashboard.getSecondPartLogBaseUrl = function(clinicKey, clinicBranchKey, apiVersion) {
        return apiVersion + '/Clinic/' + clinicKey + '/ClinicBranch/' + clinicBranchKey  + '/InfectionLogs';
    };


    InfectionDashboard.buildAssignedToPath = function(basePath,assignedTo,isClosed,sort,pageSize,pageNumber){
        return  basePath
            +'?AssignedToKey='+ assignedTo
            + '&IsClosed=' + isClosed
            + '&Sort=' + String(sort)
            + '&PageSize=' + pageSize
            + '&PageNumber=' + pageNumber;
    }

    InfectionDashboard.getInfectionLogsByClinicBranch = function(clinicKey, clinicBranchKey, dateFrom, dateTo, isClosed, sort, pageSize, pageNumber, infectionType, assignedTo, status){

        var path = InfectionDashboard.getSecondPartBaseUrlWithClinicBranch(clinicKey, clinicBranchKey, InfectionDashboard.apiVersion);
        if(assignedTo){
            return InfectionDashboard.query({
                path: InfectionDashboard.buildAssignedToPath(path,assignedTo,isClosed,sort,pageSize,pageNumber),
                url: InfectionDashboard.baseUrl,
                headers: InfectionDashboard.noCacheHeader
            });
        }
        else{
            return InfectionDashboard.query({
                path: path
                +'?ReportedDateFrom='+ dateFrom
                + '&ReportedDateTo=' + dateTo
                + '&IsClosed=' + isClosed
                + '&Sort=' + String(sort)
                + '&PageSize=' + pageSize
                + '&PageNumber=' + pageNumber
                + (infectionType >= 0 ? '&InfectionTypeKey=' + infectionType : '')
                + (status >= 0 ? '&statusOption=' + status : ''),
                url: InfectionDashboard.baseUrl,
                headers: InfectionDashboard.noCacheHeader
            });
        }
    };

    InfectionDashboard.getInfectionLogsByClinicBranchAndCaseManager = function(clinicKey, clinicBranchKey, caseManagerId,dateFrom, dateTo, isClosed, sort, pageSize, pageNumber, infectionType, assignedTo, status){

        var path = InfectionDashboard.getSecondPartBaseUrlWithClinicBranch(clinicKey, clinicBranchKey, InfectionDashboard.apiVersion);
        if(assignedTo){
            return InfectionDashboard.query({
                path: InfectionDashboard.buildAssignedToPath(path,assignedTo,isClosed,sort,pageSize,pageNumber),
                url: InfectionDashboard.baseUrl
            });
        }
        else{
            return InfectionDashboard.query({
                path: path
                + '?CaseManagerKey=' + caseManagerId
                + '&ReportedDateFrom='+ dateFrom
                + '&ReportedDateTo='+ dateTo
                + '&IsClosed=' + isClosed
                + '&Sort='+ String(sort)
                + '&PageSize=' + pageSize
                + '&PageNumber=' + pageNumber
                + (infectionType >= 0 ? '&InfectionTypeKey=' + infectionType : '')
                + (status >= 0 ? '&statusOption=' + status : ''),
                url: InfectionDashboard.baseUrl,
                headers: InfectionDashboard.noCacheHeader
            });
        }
    };


    InfectionDashboard.getInfectionLogsByClinicAndCaseManager = function(clinicKey, caseManagerId, dateFrom, dateTo, isClosed, sort, pageSize, pageNumber, infectionType, assignedTo, status){

        var path = InfectionDashboard.getSecondPartBaseUrl(clinicKey, InfectionDashboard.apiVersion)
        if(assignedTo){
            return InfectionDashboard.query({
                path: InfectionDashboard.buildAssignedToPath(path,assignedTo,isClosed,sort,pageSize,pageNumber),
                url: InfectionDashboard.baseUrl
            });
        }
        else{
            return InfectionDashboard.query({
                path: path
                + '?CaseManagerKey=' + caseManagerId
                + '&ReportedDateFrom='+ dateFrom
                + '&ReportedDateTo=' + dateTo
                + '&IsClosed=' + isClosed
                + '&Sort='+ String(sort)
                + '&PageSize=' + pageSize
                + '&PageNumber=' + pageNumber
                + (infectionType >= 0 ? '&InfectionTypeKey=' + infectionType : '')
                + (status >= 0 ? '&statusOption=' + status : ''),
                url: InfectionDashboard.baseUrl,
                headers: InfectionDashboard.noCacheHeader
            });
        }
    };

    InfectionDashboard.getInfectionLogsByClinic = function(clinicKey, dateFrom, dateTo, isClosed, sort, pageSize, pageNumber, infectionType, assignedTo, status){

        var path = InfectionDashboard.getSecondPartBaseUrl(clinicKey, InfectionDashboard.apiVersion);

        if(assignedTo){
            return InfectionDashboard.query({
                path: InfectionDashboard.buildAssignedToPath(path,assignedTo,isClosed,sort,pageSize,pageNumber),
                url: InfectionDashboard.baseUrl
            });
        }
        else{
            return InfectionDashboard.query({
                path: InfectionDashboard.getSecondPartBaseUrl(clinicKey, InfectionDashboard.apiVersion)
                + '?ReportedDateFrom='+ dateFrom
                + '&ReportedDateTo='+ dateTo
                + '&IsClosed=' + isClosed
                + '&Sort='+ String(sort)
                + '&PageSize=' + pageSize
                + '&PageNumber=' + pageNumber
                + (infectionType >= 0 ? '&InfectionTypeKey=' + infectionType : '')
                + (status >= 0 ? '&statusOption=' + status : ''),
                url: InfectionDashboard.baseUrl,
                headers: InfectionDashboard.noCacheHeader
            });
        }
    };


    InfectionDashboard.searchInfectionLogsForClinicAndCaseManager = function(clinicKey, caseManagerId, dateFrom, dateTo, isClosed, sort, pageSize, pageNumber,searchValue,infectionType, assignedTo, status){

        var path = InfectionDashboard.getSecondPartBaseUrl(clinicKey, InfectionDashboard.apiVersion);
        if(assignedTo){
            return InfectionDashboard.query({
                path: InfectionDashboard.buildAssignedToPath(path,assignedTo,isClosed,sort,pageSize,pageNumber),
                url: InfectionDashboard.baseUrl
            });
        }
        else{
            return InfectionDashboard.query({
                path: path
                + '?CaseManagerKey=' + caseManagerId
                + '&ReportedDateFrom='+ dateFrom
                + '&ReportedDateTo=' + dateTo
                + '&IsClosed=' + isClosed
                + '&Search='+ String(searchValue)
                + '&Sort='+ String(sort)
                + '&PageSize=' + pageSize
                + '&PageNumber=' + pageNumber
                + (infectionType >= 0 ? '&InfectionTypeKey=' + infectionType : '')
                + (status >= 0 ? '&statusOption=' + status : ''),
                url: InfectionDashboard.baseUrl,
                headers: InfectionDashboard.noCacheHeader
            });
        }
    };

    InfectionDashboard.searchInfectionLogsForClinicBranch = function(clinicKey, clinicBranchKey, dateFrom, dateTo, isClosed, sort, pageSize, pageNumber,searchValue, infectionType, assignedTo, status){

        var path = InfectionDashboard.getSecondPartBaseUrlWithClinicBranch(clinicKey, clinicBranchKey, InfectionDashboard.apiVersion) ;
        if(assignedTo){
            return InfectionDashboard.query({
                path: InfectionDashboard.buildAssignedToPath(path,assignedTo,isClosed,sort,pageSize,pageNumber),
                url: InfectionDashboard.baseUrl
            });
        }

        else{
            return InfectionDashboard.query({
                path: path
                +'?ReportedDateFrom='+ dateFrom
                + '&ReportedDateTo=' + dateTo
                + '&IsClosed=' + isClosed
                + '&Sort=' + String(sort)
                + '&Search='+ String(searchValue)
                + '&PageSize=' + pageSize
                + '&PageNumber=' + pageNumber
                + (infectionType >= 0 ? '&InfectionTypeKey=' + infectionType : '')
                + (status >= 0 ? '&statusOption=' + status : ''),
                url: InfectionDashboard.baseUrl,
                headers: InfectionDashboard.noCacheHeader
            });
        }
    };

    InfectionDashboard.searchInfectionLogsForClinicBranchAndCaseManager = function(clinicKey, clinicBranchKey, caseManagerId,dateFrom, dateTo, isClosed, sort, pageSize, pageNumber,searchValue, infectionType, assignedTo, status){

        var path = InfectionDashboard.getSecondPartBaseUrlWithClinicBranch(clinicKey, clinicBranchKey, InfectionDashboard.apiVersion);

        if(assignedTo){
            return InfectionDashboard.query({
                path: InfectionDashboard.buildAssignedToPath(path,assignedTo,isClosed,sort,pageSize,pageNumber),
                url: InfectionDashboard.baseUrl
            });
        }
        else{
            return InfectionDashboard.query({
                path: path
                + '?CaseManagerKey=' + caseManagerId
                + '&ReportedDateFrom='+ dateFrom
                + '&ReportedDateTo='+ dateTo
                + '&IsClosed=' + isClosed
                + '&Sort='+ String(sort)
                + '&Search='+ String(searchValue)
                + '&PageSize=' + pageSize
                + '&PageNumber=' + pageNumber
                + (infectionType >= 0 ? '&InfectionTypeKey=' + infectionType : '')
                + (status >= 0 ? '&statusOption=' + status : ''),
                url: InfectionDashboard.baseUrl,
                headers: InfectionDashboard.noCacheHeader
            });
        }
    };

    InfectionDashboard.searchInfectionLogsForClinic = function(clinicKey, dateFrom, dateTo, isClosed, sort, pageSize, pageNumber,searchValue, infectionType, assignedTo, status){

        var path = InfectionDashboard.getSecondPartBaseUrl(clinicKey, InfectionDashboard.apiVersion);
        if(assignedTo){
            return InfectionDashboard.query({
                path: InfectionDashboard.buildAssignedToPath(path,assignedTo,isClosed,sort,pageSize,pageNumber),
                url: InfectionDashboard.baseUrl
            });
        }
        else{
            return InfectionDashboard.query({
                path: path
                + '?ReportedDateFrom='+ dateFrom
                + '&ReportedDateTo='+ dateTo
                + '&IsClosed=' + isClosed
                + '&Sort='+ String(sort)
                + '&Search='+ String(searchValue)
                + '&PageSize=' + pageSize
                + '&PageNumber=' + pageNumber
                + (infectionType >= 0 ? '&InfectionTypeKey=' + infectionType : '')
                + (status >= 0 ? '&statusOption=' + status : ''),
                url: InfectionDashboard.baseUrl,
                headers: InfectionDashboard.noCacheHeader
            });
        }
    };

    InfectionDashboard.getInfectionLogKeys = function(clinicKey, clinicBranchId, caseManagerId, dateFrom, dateTo, isClosed){
        var path = angular.isString(clinicBranchId) ?
        InfectionDashboard.getSecondPartBaseUrl(clinicKey, InfectionDashboard.apiVersion) :
        InfectionDashboard.getSecondPartBaseUrlWithClinicBranch(clinicKey, clinicBranchId, InfectionDashboard.apiVersion);

        path += '/Keys';
        path += angular.isString(caseManagerId) ? '?ReportedDateFrom=' + dateFrom : '?CaseManagerKey=' + caseManagerId + '&ReportedDateFrom=' + dateFrom;
        path += '&ReportedDateTo='+ dateTo ;
        path += '&IsClosed='+ isClosed;

        return InfectionDashboard.query({
            path: path,
            url: InfectionDashboard.baseUrl,
            headers: InfectionDashboard.noCacheHeader
        });
    };

    InfectionDashboard.getMyFollowUpsInfectionLogKeys = function(clinicKey, clinicBranchId, assignedTo, isClosed){

        var path = InfectionDashboard.getSecondPartBaseUrl(clinicKey, InfectionDashboard.apiVersion)
                   +'/Keys?AssignedToKey='+ assignedTo + '&IsClosed='+ isClosed;
        return InfectionDashboard.query({
            path: path,
            url: InfectionDashboard.baseUrl,
            headers: InfectionDashboard.noCacheHeader
        });
    };

    InfectionDashboard.exportToExcel = function(clinicKey, request) {
        return InfectionDashboard.downloadFileByPost({
            path: InfectionDashboard.getSecondPartBaseUrl(clinicKey, InfectionDashboard.apiVersion) + '/Export',
            url: InfectionDashboard.baseUrl,
            data: angular.toJson(request),
            headers: {
                'Content-Type': 'application/json',
                'accept': 'application/vnd.ms-excel'
            },
            responseType: 'blob'
        });
    };

    InfectionDashboard.getExistingInfectionLog = function(clinicKey, clinicBranchKey, patientKey) {
        var path = InfectionDashboard.getSecondPartLogBaseUrl(clinicKey, clinicBranchKey, InfectionDashboard.apiVersion) + '/Verify/' + patientKey;

        return InfectionDashboard.query({
            path: path,
            url: InfectionDashboard.baseUrl,
            headers: InfectionDashboard.noCacheHeader
        });
    };

    InfectionDashboard.getInfectionLogInformation = function(clinicKey, clinicBranchKey, infectionLog) {
        var path = InfectionDashboard.getSecondPartLogBaseUrl(clinicKey, clinicBranchKey, InfectionDashboard.apiVersion) + '/History/' + infectionLog ;

        return InfectionDashboard.query({
            path: path,
            url: InfectionDashboard.baseUrl,
            headers: InfectionDashboard.noCacheHeader
        });
    };

    return InfectionDashboard;
}]);
