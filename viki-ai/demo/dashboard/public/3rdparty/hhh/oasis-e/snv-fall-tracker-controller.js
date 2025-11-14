(function(moment) {
    'use strict';

    angular.module('amng.falltracker', [
        'resources.fallTracker-patient',
        'LocalStorageModule',
        'services.ic.utils'
    ])
        .controller('FallTrackerController', controller)
        .constant('FallTrackerConstants', { 
            btnText: 'Yes, Create Fall Log',
            errorMessage: 'There was an error saving this form, Please contact support if the problem persists.',
            errorTypes: {error: 'error', warning: 'warning'}
        });

    controller.$inject = [
        'FallTrackerConstants',
        'FallTrackerPatient',
        'InfectionControlUtilsService',
        'localStorageService',
        '$window',
        '$q'
    ];


    function controller(
        FallTrackerConstants,
        FallTrackerPatient,
        InfectionControlUtilsService,
        localStorageService,
        $window,
        $q
    ) {
        var vm = angular.extend(this, {
            //members
            addButtonDisabled: true,
            caseManagerId: null,
            clinicId: null,
            clinicBranchId: null,
            incidentsUrl: null,
            episodeKey: null,
            errorList: [],
            infectionTypes:[],
            patientId: null,
            patientFalls:[],
            physicianId: null,
            reportedById:null,
            saveFormFunction: 'modifyForm',
            FallTrackerConstants: FallTrackerConstants,
            injuryOptions : {
                 0: 'No Injury' ,
                 1: 'Injury (Except Major)',
                 2:'Major Injury' ,
                 3: 'Not Selected'
            },
            initialize: initialize,
            saveForm: saveForm,
            setErrorMessage: setErrorMessage,
            haveErrors: haveErrors,
            showMessages: showMessages,
            addNewFall: addNewFall,
            applySaveFormFunction: applySaveFormFunction,
            editForm: editForm,
            deleteFallLog: deleteFallLog
        });



        function initialize(
            patientId,
            physicianId,
            caseManagerAmUserKey,
            caseManagerUsersKey,
            reportedById,
            clinicId,
            clinicBranchId,
            incidentsUrl,
            episodeKey,
            saveFormFunction
        ){
            vm.incidentsUrl = incidentsUrl;
            vm.patientId = patientId;
            vm.physicianId = physicianId;
            vm.caseManagerId = InfectionControlUtilsService.fixCaseManagerUserKey({ AMUSERKEY: caseManagerAmUserKey, USERSKEY: caseManagerUsersKey});
            vm.reportedById = reportedById;
            vm.clinicId = clinicId;
            vm.clinicBranchId = clinicBranchId;
            vm.episodeKey = episodeKey;
            vm.saveFormFunction = saveFormFunction;
            FallTrackerPatient.getFallsByPatient(vm.clinicId, vm.clinicBranchId, vm.episodeKey, vm.patientId, moment('1800-01-01').format('YYYY-MM-DD HH:mm:ss')).then(function(response) {
                response.result.data.forEach(function(fall) {
                    vm.patientFalls.push({
                        dateFallOcurred: moment(fall.fallLogDate).format('MM-DD-YYYY'),
                        injuryOption: vm.injuryOptions[fall.injuryOption],
                        fallStatus: fall.fallStatus,
                        fallLogKey: fall.fallLogKey,
                        fallLogAuditUserName: fall.fallLogAuditUserName
                    });
                });
            });
        }

        function addNewFall(){
            vm.saveForm('add');
        }
        function editForm(fallLogKey){
            vm.saveForm('edit',fallLogKey);
        }
        function deleteFallLog(fallLogKey){
            var fallKey= fallLogKey;
            FallTrackerPatient.deleteFall(fallLogKey,vm.clinicId, vm.clinicBranchId).then(function(response) {
                if(response.statusCode == 200){
                    vm.patientFalls.forEach(function (value,index) {
                        if(value.fallLogKey == fallKey){
                            vm.patientFalls.splice(index,1);
                        }
                    });
                }
            });
        }

        function saveForm(action, fallKey) {
            if ($window[vm.saveFormFunction]) {
                var params
                var destination = "";
                if (vm.saveFormFunction === 'validateSubmit') {
                    if(action === 'add'){
                        destination = vm.incidentsUrl+'/newincident/'+ vm.episodeKey +'/'+ vm.patientId;
                    } else if(action == 'edit'){
                        destination = vm.incidentsUrl+'/editincident/' + fallKey + '/clinicBranch/' + vm.clinicBranchId + '/clinic/' + vm.clinicId;    
                    } 
                    params = [undefined, 'Save', destination, undefined];
                } else if(vm.saveFormFunction === 'modifyForm'){
                    
                    if(action == 'add'){
                        destination = vm.incidentsUrl+'/newincident/'+ vm.episodeKey +'/'+ vm.patientId;
                    } else if(action == 'edit'){
                        destination = vm.incidentsUrl+'/editincident/' + fallKey + '/clinicBranch/' + vm.clinicBranchId + '/clinic/' + vm.clinicId;
                    }
                    params = ['Save', destination];
                }else {
                    vm.setErrorMessage();
                    vm.showMessages();
                    return false;                    
                }

                vm.applySaveFormFunction(vm.saveFormFunction, params)
            } else {
                vm.setErrorMessage();
                vm.showMessages();
            }
        }
        function applySaveFormFunction(fn, params) {
            $window[fn].apply(null, params);
        }
        function setErrorMessage() {
            vm.setErrorList([vm.FallTrackerConstants.errorMessage], vm.FallTrackerConstants.errorTypes.error);
        }

        function showMessages() {
            if (vm.haveErrors()) {
                vm.showErrorMssg = true;
            }
        }
        function haveErrors() {
            return (vm.errorList.length);
        }
    }
}) (moment);
